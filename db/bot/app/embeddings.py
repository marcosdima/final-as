import asyncio
import hashlib
import logging
import math
from typing import List, Optional

from app.config import settings

logger = logging.getLogger(__name__)

_embedding_model: Optional[object] = None


def _get_fastembed_model():
    """Lazy-load FastEmbed model to keep application startup fast."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from fastembed import TextEmbedding

            logger.info("Loading embedding model: %s", settings.EMBEDDING_MODEL)
            _embedding_model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
        except Exception as exc:
            logger.warning(
                "Could not initialize FastEmbed (%s). Using deterministic fallback generator.",
                exc,
            )
            _embedding_model = False
    return _embedding_model


def _fallback_embedding(text: str, dim: int = 384) -> List[float]:
    """Deterministic 384-d fallback vector generator for offline environments."""
    tokens = text.lower().split()
    vec = [0.0] * dim
    for tok in tokens:
        h = int(hashlib.sha256(tok.encode("utf-8")).hexdigest(), 16)
        for i in range(dim):
            bit = (h >> (i % 64)) & 1
            weight = 1.0 if bit else -1.0
            vec[i] += weight / (1.0 + (i % 7))

    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        return [1.0 / math.sqrt(dim)] * dim
    return [round(x / norm, 6) for x in vec]


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate normalized embeddings for a list of texts (CPU-bound)."""
    if not texts:
        return []

    model = _get_fastembed_model()
    if model:
        try:
            generator = model.embed(texts)
            return [list(map(float, vec)) for vec in generator]
        except Exception as exc:
            logger.error("FastEmbed embedding error (%s). Falling back.", exc)

    return [_fallback_embedding(t, settings.EMBEDDING_DIM) for t in texts]


def embed_query(query: str) -> List[float]:
    """Generate embedding vector for a search query."""
    return embed_texts([query])[0]


async def embed_texts_async(texts: List[str]) -> List[List[float]]:
    """Run text embedding generation in a worker thread to avoid blocking the event loop."""
    return await asyncio.to_thread(embed_texts, texts)


async def embed_query_async(query: str) -> List[float]:
    """Run query embedding generation in a worker thread."""
    return await asyncio.to_thread(embed_query, query)
