"""
PDF Loader Service.
Extracts text from PDF files using PyPDF and chunks text into overlapping segments.
"""

import logging
import os
from typing import List, Tuple

import aiofiles
from pypdf import PdfReader

from config import settings

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file using PyPDF.

    Args:
        file_path: Absolute or relative path to the PDF file.

    Returns:
        Concatenated text content of all pages.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        Exception: If PDF parsing fails.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(file_path)
        pages_text = []
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text.strip())
            except Exception as e:
                logger.warning(f"Could not extract text from page {page_num}: {e}")
                continue

        full_text = "\n\n".join(pages_text)
        logger.info(f"Extracted {len(full_text)} characters from {file_path} ({len(reader.pages)} pages)")
        return full_text

    except Exception as e:
        logger.error(f"Failed to read PDF {file_path}: {e}")
        raise


def chunk_text(
    text: str,
    chunk_size: int = None,
    overlap: int = None,
) -> List[str]:
    """
    Split text into overlapping chunks for embedding.

    Args:
        text: The full text to split.
        chunk_size: Maximum number of characters per chunk. Defaults to settings.CHUNK_SIZE.
        overlap: Number of characters to overlap between chunks. Defaults to settings.CHUNK_OVERLAP.

    Returns:
        List of text chunks.
    """
    if chunk_size is None:
        chunk_size = settings.CHUNK_SIZE
    if overlap is None:
        overlap = settings.CHUNK_OVERLAP

    if not text or not text.strip():
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]

        # Avoid tiny trailing chunks
        if chunk.strip():
            chunks.append(chunk.strip())

        if end >= text_length:
            break

        start = end - overlap  # Move back by overlap amount

    logger.info(f"Text chunked into {len(chunks)} chunks (size={chunk_size}, overlap={overlap})")
    return chunks


async def load_and_chunk_pdf(file_path: str) -> Tuple[str, List[str]]:
    """
    Asynchronously extract and chunk text from a PDF file.

    Args:
        file_path: Path to the PDF file.

    Returns:
        Tuple of (full_text, list_of_chunks).
    """
    # PDF reading is CPU-bound so we call the sync function directly
    # For production, consider running in a thread pool executor
    full_text = extract_text_from_pdf(file_path)
    chunks = chunk_text(full_text)
    return full_text, chunks
