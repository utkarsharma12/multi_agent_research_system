"""
Vector Store module.
Manages a ChromaDB collection for storing and retrieving document embeddings.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from config import settings
from rag.embeddings import embed_texts, embed_query

logger = logging.getLogger(__name__)

# Singleton ChromaDB client and collection
_client: Optional[chromadb.PersistentClient] = None
_collection: Optional[chromadb.Collection] = None


def _get_client() -> chromadb.PersistentClient:
    """
    Lazily initialize and return the ChromaDB persistent client singleton.

    Returns:
        chromadb.PersistentClient: The initialized ChromaDB client.
    """
    global _client
    if _client is None:
        logger.info(f"Initializing ChromaDB client at: {settings.CHROMA_PERSIST_DIR}")
        _client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        logger.info("ChromaDB client initialized")
    return _client


def _get_collection() -> chromadb.Collection:
    """
    Lazily get or create the research documents ChromaDB collection.

    Returns:
        chromadb.Collection: The ChromaDB collection instance.
    """
    global _collection
    if _collection is None:
        client = _get_client()
        _collection = client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"ChromaDB collection '{settings.CHROMA_COLLECTION}' ready")
    return _collection


def init_vector_store() -> None:
    """
    Initialize the vector store by connecting to ChromaDB and creating the collection.
    Should be called during application startup.
    """
    _get_collection()
    logger.info("Vector store initialized successfully")


def add_documents(
    texts: List[str],
    metadatas: Optional[List[Dict[str, Any]]] = None,
    ids: Optional[List[str]] = None,
) -> List[str]:
    """
    Add text documents to the ChromaDB vector collection.
    Embeddings are generated internally using the sentence-transformers model.

    Args:
        texts: List of text strings to store.
        metadatas: Optional list of metadata dicts, one per text.
        ids: Optional list of unique string IDs. Auto-generated if not provided.

    Returns:
        List of document IDs that were inserted.

    Raises:
        ValueError: If texts is empty.
    """
    if not texts:
        raise ValueError("Cannot add empty list of texts to vector store")

    if ids is None:
        ids = [str(uuid.uuid4()) for _ in texts]

    if metadatas is None:
        metadatas = [{} for _ in texts]

    # Generate embeddings
    embeddings = embed_texts(texts)

    collection = _get_collection()
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    logger.info(f"Added {len(texts)} documents to ChromaDB collection '{settings.CHROMA_COLLECTION}'")
    return ids


def similarity_search(
    query: str,
    k: int = 5,
    where: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Perform a cosine similarity search against the vector store.

    Args:
        query: The query text to search for.
        k: Number of top results to return. Defaults to 5.
        where: Optional ChromaDB metadata filter dict.

    Returns:
        List of result dicts, each containing:
            - id (str): Document ID
            - document (str): The stored text
            - metadata (dict): Associated metadata
            - distance (float): Cosine distance (lower = more similar)
    """
    if not query or not query.strip():
        return []

    query_embedding = embed_query(query)
    collection = _get_collection()

    query_kwargs: Dict[str, Any] = {
        "query_embeddings": [query_embedding],
        "n_results": min(k, collection.count() or 1),
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        query_kwargs["where"] = where

    try:
        results = collection.query(**query_kwargs)
    except Exception as e:
        logger.error(f"ChromaDB query failed: {e}")
        return []

    # Flatten the nested results structure
    output = []
    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for doc_id, doc, meta, dist in zip(ids, documents, metadatas, distances):
        output.append(
            {
                "id": doc_id,
                "document": doc,
                "metadata": meta or {},
                "distance": dist,
            }
        )

    logger.info(f"Similarity search returned {len(output)} results for query: '{query[:60]}...'")
    return output


def delete_documents(ids: List[str]) -> None:
    """
    Delete documents from the ChromaDB collection by their IDs.

    Args:
        ids: List of document IDs to delete.
    """
    if not ids:
        return

    collection = _get_collection()
    collection.delete(ids=ids)
    logger.info(f"Deleted {len(ids)} documents from ChromaDB")


def get_collection_count() -> int:
    """
    Return the total number of documents in the ChromaDB collection.

    Returns:
        int: Number of stored document chunks.
    """
    try:
        return _get_collection().count()
    except Exception:
        return 0
