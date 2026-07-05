import httpx
import redis
from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])


def _check_redis() -> bool:
    try:
        client = redis.from_url(settings.redis_url, socket_connect_timeout=2)
        return client.ping()
    except Exception:
        return False


def _check_qdrant() -> bool:
    try:
        response = httpx.get(f"{settings.qdrant_url}/collections", timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False


def _check_ollama() -> bool:
    try:
        response = httpx.get(f"{settings.ollama_url}/api/tags", timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False


def _check_ollama_model() -> bool:
    try:
        response = httpx.get(f"{settings.ollama_url}/api/tags", timeout=2.0)
        if response.status_code != 200:
            return False
        models = response.json().get("models", [])
        return any(
            model.get("name", "").startswith(settings.ollama_model) for model in models
        )
    except Exception:
        return False


@router.get("/health")
def health():
    services = {
        "redis": _check_redis(),
        "qdrant": _check_qdrant(),
        "ollama": _check_ollama(),
        "ollama_model": _check_ollama_model(),
    }
    core_ok = services["redis"] and services["qdrant"] and services["ollama"]
    return {
        "status": "ok" if core_ok and services["ollama_model"] else "degraded",
        "services": services,
        "config": {
            "redis_url": settings.redis_url,
            "qdrant_url": settings.qdrant_url,
            "ollama_url": settings.ollama_url,
            "ollama_model": settings.ollama_model,
            "redis_ttl_seconds": settings.redis_ttl_seconds,
            "semantic_threshold": settings.semantic_threshold,
            "rag_top_k": settings.rag_top_k,
            "embedding_model": settings.embedding_model,
        },
    }
