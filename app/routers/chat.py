import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest, ChatResponse
from app.services.cache import get_exact_cache, set_exact_cache
from app.services.llm import LLMError, generate_answer, stream_answer
from app.services.semantic_cache import get_semantic_cache, set_semantic_cache

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="message cannot be empty")

    # Tier 1: Redis exact-match cache
    exact = get_exact_cache(message)
    if exact is not None:
        if request.stream:
            return StreamingResponse(
                _sse_cached(exact, "exact"),
                media_type="text/event-stream",
            )
        return ChatResponse(answer=exact, cache_hit=True, cache_type="exact")

    # Tier 2: Qdrant semantic cache
    semantic = get_semantic_cache(message)
    if semantic is not None:
        set_exact_cache(message, semantic)  # warm Redis for next identical ask
        if request.stream:
            return StreamingResponse(
                _sse_cached(semantic, "semantic"),
                media_type="text/event-stream",
            )
        return ChatResponse(answer=semantic, cache_hit=True, cache_type="semantic")

    if request.stream:
        return StreamingResponse(
            _sse_stream_and_cache(message),
            media_type="text/event-stream",
        )

    try:
        answer = await generate_answer(message)
    except LLMError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    set_exact_cache(message, answer)
    set_semantic_cache(message, answer)
    return ChatResponse(answer=answer, cache_hit=False, cache_type=None)


async def _sse_cached(answer: str, cache_type: str):
    yield f"data: {json.dumps({'token': answer, 'cache_hit': True, 'cache_type': cache_type})}\n\n"
    yield f"data: {json.dumps({'done': True, 'cache_hit': True, 'cache_type': cache_type})}\n\n"


async def _sse_stream_and_cache(message: str):
    chunks: list[str] = []
    try:
        async for token in stream_answer(message):
            chunks.append(token)
            yield f"data: {json.dumps({'token': token, 'cache_hit': False})}\n\n"
        answer = "".join(chunks)
        set_exact_cache(message, answer)
        set_semantic_cache(message, answer)
        yield f"data: {json.dumps({'done': True, 'cache_hit': False})}\n\n"
    except LLMError as exc:
        yield f"data: {json.dumps({'error': str(exc)})}\n\n"
