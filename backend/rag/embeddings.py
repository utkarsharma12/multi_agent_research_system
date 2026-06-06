"""
Embeddings module.
Uses Google Gemini API to generate vector embeddings for text and queries,
saving hundreds of MBs of RAM compared to local sentence-transformers.
"""

import logging
from typing import List

import google.generativeai as genai

from config import settings

logger = logging.getLogger(__name__)

# Configure the API key
if settings.GOOGLE_API_KEY:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
else:
    logger.warning("GOOGLE_API_KEY is not set. Embeddings will fail.")


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of text strings using Gemini.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors (each a list of floats).
    """
    if not texts:
        raise ValueError("Cannot embed an empty list of texts")

    logger.debug(f"Generating embeddings for {len(texts)} texts via Gemini API...")
    
    response = genai.embed_content(
        model="models/text-embedding-004",
        content=texts,
        task_type="retrieval_document"
    )
    
    return response['embedding']


def embed_query(query: str) -> List[float]:
    """
    Generate an embedding for a single query string using Gemini.

    Args:
        query: The query text to embed.

    Returns:
        A single embedding vector as a list of floats.
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    response = genai.embed_content(
        model="models/text-embedding-004",
        content=query,
        task_type="retrieval_query"
    )
    
    return response['embedding']
