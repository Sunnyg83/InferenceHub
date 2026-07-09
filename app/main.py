import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.routers import health
from app.services.embeddings import load_embedding_model
from app.services.qdrant import ensure_collections

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading embedding model: %s", settings.embedding_model)
    load_embedding_model()
    logger.info("Ensuring Qdrant collections exist")
    ensure_collections()
    yield


app = FastAPI(title="InferenceHub", lifespan=lifespan)
app.include_router(health.router)


@app.get("/")
def root():
    return {
        "name": "InferenceHub",
        "description": "LLM inference API with caching, RAG, and monitoring",
        "health": "/health",
        "model": settings.ollama_model,
        "embedding_model": settings.embedding_model,
    }
