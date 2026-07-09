from sentence_transformers import SentenceTransformer

from app.config import settings

_model: SentenceTransformer | None = None


def load_embedding_model() -> None:
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)


def embed_text(text: str) -> list[float]:
    if _model is None:
        raise RuntimeError("Embedding model not loaded. Call load_embedding_model() at startup.")
    return _model.encode(text, normalize_embeddings=True).tolist()
