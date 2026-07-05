from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup hook — later phases will load embedding models here.
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
    }
