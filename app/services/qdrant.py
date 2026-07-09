from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.config import settings

SEMANTIC_CACHE_COLLECTION = "semantic_cache"
DOCUMENTS_COLLECTION = "documents"

COLLECTIONS = [SEMANTIC_CACHE_COLLECTION, DOCUMENTS_COLLECTION]


def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def ensure_collections() -> None:
    client = get_qdrant_client()
    for collection_name in COLLECTIONS:
        if client.collection_exists(collection_name):
            continue
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=settings.embedding_dim,
                distance=Distance.COSINE,
            ),
        )


def collections_ready() -> dict[str, bool]:
    client = get_qdrant_client()
    return {
        name: client.collection_exists(name)
        for name in COLLECTIONS
    }
