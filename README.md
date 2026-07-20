# InferenceHub

A local LLM inference API. Ask questions through HTTP, run the model on your machine with Ollama, and speed up repeat questions with Redis caching.

## What it does right now

- `POST /chat` — ask a question, get an answer from Qwen3
- Redis exact cache — same question twice returns the saved answer (no second model call)
- Docker Compose runs FastAPI, Redis, Qdrant, Ollama, Prometheus, and Grafana

## Quick start

```bash
docker compose up -d --build
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is UCLA?"}'
```

Second identical call should be fast and return `"cache_hit": true`.

## Stack

FastAPI · Redis · Qdrant · Ollama (Qwen3) · Docker · Prometheus · Grafana
