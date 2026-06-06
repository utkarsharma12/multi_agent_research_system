"""
RAG Retriever module.
High-level retriever that embeds a query and fetches relevant context from ChromaDB.
"""

import logging
from typing import List, Dict, Any

from rag.vector_store import similarity_search
from config import settings

logger = logging.getLogger(__name__)


def retrieve_context(query: str, k: int = None) -> str:
    """
    Retrieve relevant document context from the vector store for a given query.

    Embeds the query, runs a similarity search in ChromaDB, and formats the
    results into a single context string suitable for LLM consumption.

    Args:
        query: The research query or question.
        k: Number of top-k results to retrieve. Defaults to settings.TOP_K_RESULTS.

    Returns:
        Formatted context string with numbered document excerpts,
        or an empty string if no relevant documents are found.
    """
    if k is None:
        k = settings.TOP_K_RESULTS

    try:
        results = similarity_search(query=query, k=k)
    except Exception as e:
        logger.error(f"Retriever failed for query '{query}': {e}")
        return ""

    if not results:
        logger.info(f"No relevant documents found for query: '{query[:60]}'")
        return ""

    context_parts = []
    for i, result in enumerate(results, start=1):
        doc_text = result.get("document", "")
        metadata = result.get("metadata", {})
        source = metadata.get("source", metadata.get("title", "Unknown source"))

        if doc_text.strip():
            context_parts.append(
                f"[Document {i}] (Source: {source})\n{doc_text.strip()}"
            )

    context = "\n\n---\n\n".join(context_parts)
    logger.info(
        f"Retrieved {len(results)} context chunks for query '{query[:60]}...' "
        f"({len(context)} chars total)"
    )
    return context


def retrieve_raw_results(query: str, k: int = None) -> List[Dict[str, Any]]:
    """
    Retrieve raw similarity search results for a query.

    Args:
        query: The research query.
        k: Number of results to return.

    Returns:
        List of raw result dicts from the vector store.
    """
    if k is None:
        k = settings.TOP_K_RESULTS

    try:
        return similarity_search(query=query, k=k)
    except Exception as e:
        logger.error(f"Raw retrieval failed: {e}")
        return []
