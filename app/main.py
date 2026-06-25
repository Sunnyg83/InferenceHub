import httpx
import redis
from fastapi import FastAPI

from app.config import OLLAMA_MODEL, OLLAMA_URL, QDRANT_URL, REDIS_URL

app = FastAPI(title="InferenceHub")


def _check_redis() -> bool:
    try:
        client = redis.from_url(REDIS_URL, socket_connect_timeout=2)
        return client.ping()
    except Exception:
        return False


def _check_qdrant() -> bool:
    try:
        response = httpx.get(f"{QDRANT_URL}/collections", timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False


def _check_ollama() -> bool:
    try:
        response = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False


def _check_ollama_model() -> bool:
    try:
        response = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=2.0)
        if response.status_code != 200:
            return False
        models = response.json().get("models", [])
        return any(model.get("name", "").startswith(OLLAMA_MODEL) for model in models)
    except Exception:
        return False


@app.get("/health")
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
        "network": {
            "redis_url": REDIS_URL,
            "qdrant_url": QDRANT_URL,
            "ollama_url": OLLAMA_URL,
            "ollama_model": OLLAMA_MODEL,
        },
    }
