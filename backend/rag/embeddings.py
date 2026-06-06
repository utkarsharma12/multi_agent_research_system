"""
Embeddings module.
Uses sentence-transformers to generate vector embeddings for text and queries.
"""

import logging
from typing import List

from sentence_transformers import SentenceTransformer

from config import settings

logger = logging.getLogger(__name__)

# Singleton model instance — loaded once on module import
_model: SentenceTransformer = None


def _get_model() -> SentenceTransformer:
    """
    Lazily load and return the SentenceTransformer model singleton.

    Returns:
        SentenceTransformer: The loaded embedding model.
    """
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully")
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of text strings.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors (each a list of floats).

    Raises:
        ValueError: If texts list is empty.
    """
    if not texts:
        raise ValueError("Cannot embed an empty list of texts")

    model = _get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    logger.debug(f"Generated embeddings for {len(texts)} texts, dim={embeddings.shape[1]}")
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """
    Generate an embedding for a single query string.

    Args:
        query: The query text to embed.

    Returns:
        A single embedding vector as a list of floats.

    Raises:
        ValueError: If query is empty or whitespace only.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    model = _get_model()
    embedding = model.encode(query, convert_to_numpy=True, show_progress_bar=False)
    return embedding.tolist()
