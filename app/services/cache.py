import hashlib
import json

import redis

from app.config import settings

_client: redis.Redis | None = None

# Simple counters (Prometheus will use these later)
cache_hits = 0
cache_misses = 0


def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(settings.redis_url, decode_responses=True)
    return _client


def _cache_key(message: str) -> str:
    normalized = message.strip().lower()
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"cache:exact:{digest}"


def get_exact_cache(message: str) -> str | None:
    """Return cached answer for an exact (normalized) question, or None."""
    global cache_hits, cache_misses
    key = _cache_key(message)
    value = get_redis().get(key)
    if value is None:
        cache_misses += 1
        return None
    cache_hits += 1
    data = json.loads(value)
    return data.get("answer")


def set_exact_cache(message: str, answer: str) -> None:
    """Store answer in Redis with configurable TTL."""
    key = _cache_key(message)
    payload = json.dumps({"answer": answer})
    get_redis().setex(key, settings.redis_ttl_seconds, payload)
