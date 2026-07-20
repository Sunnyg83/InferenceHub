import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest, ChatResponse
from app.services.cache import get_exact_cache, set_exact_cache
from app.services.llm import LLMError, generate_answer, stream_answer

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="message cannot be empty")

    cached = get_exact_cache(message)
    if cached is not None:
        if request.stream:
            return StreamingResponse(
                _sse_cached(cached),
                media_type="text/event-stream",
            )
        return ChatResponse(answer=cached, cache_hit=True)

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
    return ChatResponse(answer=answer, cache_hit=False)


async def _sse_cached(answer: str):
    yield f"data: {json.dumps({'token': answer, 'cache_hit': True})}\n\n"
    yield f"data: {json.dumps({'done': True, 'cache_hit': True})}\n\n"


async def _sse_stream_and_cache(message: str):
    chunks: list[str] = []
    try:
        async for token in stream_answer(message):
            chunks.append(token)
            yield f"data: {json.dumps({'token': token, 'cache_hit': False})}\n\n"
        answer = "".join(chunks)
        set_exact_cache(message, answer)
        yield f"data: {json.dumps({'done': True, 'cache_hit': False})}\n\n"
    except LLMError as exc:
        yield f"data: {json.dumps({'error': str(exc)})}\n\n"
