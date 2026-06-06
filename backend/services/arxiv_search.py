"""
ArXiv Search Service.
Searches academic papers on arXiv and returns structured metadata.
"""

import logging
from typing import List, Dict, Any

import arxiv

logger = logging.getLogger(__name__)


def search_arxiv(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search arXiv for academic papers matching the query.

    Args:
        query: The academic search query.
        max_results: Maximum number of papers to return. Defaults to 5.

    Returns:
        List of dicts, each containing:
            - title (str): Paper title
            - authors (List[str]): List of author names
            - abstract (str): Paper abstract
            - url (str): Link to the arXiv paper page
            - published (str): Publication date as ISO string
    """
    results = []

    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        papers = list(client.results(search))

        for paper in papers:
            authors = [author.name for author in paper.authors]
            results.append(
                {
                    "title": paper.title,
                    "authors": authors,
                    "abstract": paper.summary.replace("\n", " ").strip(),
                    "url": paper.entry_id,
                    "published": paper.published.isoformat() if paper.published else "Unknown",
                }
            )

        logger.info(f"ArXiv search for '{query}' returned {len(results)} papers")

    except Exception as e:
        logger.error(f"ArXiv search failed for query '{query}': {e}")
        results = []

    return results


async def async_search_arxiv(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Async wrapper for arXiv search.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return.

    Returns:
        List of {title, authors, abstract, url, published} dicts.
    """
    return search_arxiv(query, max_results=max_results)
