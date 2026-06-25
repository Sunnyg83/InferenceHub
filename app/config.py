import os

# Inside Docker, services reach each other by service name (not localhost).
# From your Mac/browser, use localhost and the mapped ports instead.

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3")
