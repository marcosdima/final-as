import logging
import math
import hashlib
from typing import List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

_embedding_model: Optional[object] = None


def _get_fastembed_model():
    """
    Carga diferida (lazy load) del modelo FastEmbed para optimizar el arranque.
    """
    global _embedding_model
    if _embedding_model is None:
        try:
            from fastembed import TextEmbedding
            logger.info("Cargando modelo de embeddings: %s", settings.EMBEDDING_MODEL)
            _embedding_model = TextEmbedding(model_name=settings.EMBEDDING_MODEL)
        except Exception as e:
            logger.warning(
                "No se pudo inicializar FastEmbed (%s). Se usará el generador determinista fallback.", e
            )
            _embedding_model = False
    return _embedding_model


def _fallback_embedding(text: str, dim: int = 384) -> List[float]:
    """
    Generador determinista pseudo-semántico de 384 dimensiones.
    Garantiza que el servicio funcione sin conexión o sin descargar pesos.
    """
    tokens = text.lower().split()
    vec = [0.0] * dim
    for tok in tokens:
        h = int(hashlib.sha256(tok.encode("utf-8")).hexdigest(), 16)
        for i in range(dim):
            # Proyección pseudoaleatoria basada en bits de hash
            bit = (h >> (i % 64)) & 1
            weight = 1.0 if bit else -1.0
            vec[i] += weight / (1.0 + (i % 7))

    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        return [1.0 / math.sqrt(dim)] * dim
    return [round(x / norm, 6) for x in vec]


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Genera embeddings normalizados para una lista de textos.
    """
    if not texts:
        return []

    model = _get_fastembed_model()
    if model:
        try:
            generator = model.embed(texts)
            embeddings = [list(map(float, vec)) for vec in generator]
            return embeddings
        except Exception as e:
            logger.error("Error al generar embeddings con FastEmbed: %s. Aplicando fallback.", e)

    return [_fallback_embedding(t, settings.EMBEDDING_DIM) for t in texts]


def embed_query(query: str) -> List[float]:
    """
    Genera el vector de embedding para una consulta de búsqueda.
    """
    vectors = embed_texts([query])
    return vectors[0]
