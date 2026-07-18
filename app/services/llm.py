import json
from collections.abc import AsyncIterator

import httpx

from app.config import settings


class LLMError(Exception):
    """Raised when Ollama is unreachable or returns an error."""


async def generate_answer(message: str) -> str:
    """Call Ollama and return the full answer text."""
    chunks: list[str] = []
    async for token in stream_answer(message):
        chunks.append(token)
    return "".join(chunks)


async def stream_answer(message: str) -> AsyncIterator[str]:
    """Stream tokens from Ollama (Qwen3) one chunk at a time."""
    payload = {
        "model": settings.ollama_model,
        "messages": [{"role": "user", "content": message}],
        "stream": True,
    }

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
            async with client.stream(
                "POST",
                f"{settings.ollama_url}/api/chat",
                json=payload,
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    raise LLMError(
                        f"Ollama error {response.status_code}: {body.decode(errors='replace')}"
                    )

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    if data.get("error"):
                        raise LLMError(str(data["error"]))
                    content = data.get("message", {}).get("content")
                    if content:
                        yield content
                    if data.get("done"):
                        break
    except httpx.RequestError as exc:
        raise LLMError(f"Cannot reach Ollama at {settings.ollama_url}: {exc}") from exc
