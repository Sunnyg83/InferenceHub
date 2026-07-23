import uuid
from datetime import datetime, timezone

from qdrant_client.models import PointStruct

from app.config import settings
from app.services.embeddings import embed_text
from app.services.qdrant import SEMANTIC_CACHE_COLLECTION, get_qdrant_client

semantic_cache_hits = 0


def get_semantic_cache(message: str) -> str | None:
    """Return a cached answer if a similar question exists above the threshold."""
    global semantic_cache_hits
    client = get_qdrant_client()
    vector = embed_text(message)

    response = client.query_points(
        collection_name=SEMANTIC_CACHE_COLLECTION,
        query=vector,
        limit=1,
        score_threshold=settings.semantic_threshold,
    )
    points = response.points
    if not points:
        return None

    semantic_cache_hits += 1
    return points[0].payload.get("answer")


def set_semantic_cache(message: str, answer: str) -> None:
    """Store question embedding + answer in the semantic_cache collection."""
    client = get_qdrant_client()
    vector = embed_text(message)
    client.upsert(
        collection_name=SEMANTIC_CACHE_COLLECTION,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "question": message,
                    "answer": answer,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                },
            )
        ],
    )
