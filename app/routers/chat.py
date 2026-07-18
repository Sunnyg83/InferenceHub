import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest, ChatResponse
from app.services.llm import LLMError, generate_answer, stream_answer

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(request: ChatRequest):
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="message cannot be empty")

    if request.stream:
        return StreamingResponse(
            _sse_stream(message),
            media_type="text/event-stream",
        )

    try:
        answer = await generate_answer(message)
    except LLMError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ChatResponse(answer=answer)


async def _sse_stream(message: str):
    try:
        async for token in stream_answer(message):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"
    except LLMError as exc:
        yield f"data: {json.dumps({'error': str(exc)})}\n\n"
