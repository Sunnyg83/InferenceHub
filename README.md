# InferenceHub

A local LLM inference API. Ask questions through HTTP, run the model on your machine with Ollama, and speed up repeat/similar questions with caching.

## What it does right now

- `POST /chat` — ask a question, get an answer from Qwen3
- Redis exact cache — same question twice returns the saved answer
- Qdrant semantic cache — similar questions (e.g. "What is UCLA?" / "Tell me about UCLA") can reuse an answer
- Docker Compose runs FastAPI, Redis, Qdrant, Ollama, Prometheus, and Grafana

## Quick start

```bash
docker compose up -d --build
curl http://localhost:8000/health
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is UCLA?"}'
```

- Second identical call → `"cache_type": "exact"` (very fast)
- Similar rephrased call → `"cache_type": "semantic"` (fast, no LLM)

## Stack

FastAPI · Redis · Qdrant · Ollama (Qwen3) · Docker · Prometheus · Grafana
