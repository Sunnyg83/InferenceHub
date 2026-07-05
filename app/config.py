from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central config for all services and tunable pipeline values."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Service URLs — inside Docker use service names, not localhost.
    redis_url: str = "redis://redis:6379"
    qdrant_url: str = "http://qdrant:6333"
    ollama_url: str = "http://ollama:11434"
    prometheus_url: str = "http://prometheus:9090"

    # Model serving
    ollama_model: str = "qwen3"

    # Caching (used in Phase 5–6)
    redis_ttl_seconds: int = 3600
    semantic_threshold: float = 0.90

    # RAG (used in Phase 7–8)
    rag_top_k: int = 5
    embedding_model: str = "all-MiniLM-L6-v2"


settings = Settings()
