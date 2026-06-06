"""
Researcher Agent.
LangGraph node that gathers raw research data using web search, arXiv, and RAG retriever.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from services.web_search import search_web
from services.arxiv_search import search_arxiv
from rag.retriever import retrieve_context

logger = logging.getLogger(__name__)


def researcher_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph researcher node. Collects raw research data for all planned steps.

    Uses:
    - DuckDuckGo web search for current information
    - ArXiv for academic papers
    - ChromaDB RAG retriever for uploaded documents

    Args:
        state: Workflow state containing 'query', 'plan', and 'current_step'.

    Returns:
        Updated state with 'research_data' (list of source dicts).
    """
    query = state.get("query", "")
    plan = state.get("plan", [query])
    research_data: List[Dict[str, Any]] = []

    logger.info(f"[Researcher] Starting research for {len(plan)} plan steps")
    state["agent_status"] = "researching"

    try:
        # 1. Gather from RAG (uploaded documents)
        logger.info("[Researcher] Querying RAG vector store...")
        try:
            rag_context = retrieve_context(query=query, k=5)
            if rag_context:
                research_data.append(
                    {
                        "source_type": "rag",
                        "title": "Uploaded Documents Context",
                        "content": rag_context,
                        "url": None,
                        "relevance": "direct",
                    }
                )
        except Exception as e:
            logger.error(f"[Researcher] Error querying RAG vector store: {e}")

        # 2. Execute contextual search for each planned step
        for i, step_data in enumerate(plan):
            # Handle potential backward compatibility if step is a string
            if isinstance(step_data, str):
                query_str = step_data
                source = "web"
            else:
                query_str = step_data.get("query", query)
                source = step_data.get("source", "web")

            logger.info(f"[Researcher] Executing {source} search for step {i+1}: '{query_str[:60]}'")

            if source == "arxiv":
                arxiv_results = search_arxiv(query=query_str, max_results=5)
                for paper in arxiv_results:
                    research_data.append(
                        {
                            "source_type": "arxiv",
                            "title": paper.get("title", "Academic Paper"),
                            "content": paper.get("abstract", ""),
                            "url": paper.get("url", ""),
                            "authors": paper.get("authors", []),
                            "published": paper.get("published", "Unknown"),
                        }
                    )
            else:
                # Default to web search
                web_results = search_web(query=query_str, max_results=5)
                for result in web_results:
                    research_data.append(
                        {
                            "source_type": "web",
                            "title": result.get("title", "Web Result"),
                            "content": result.get("snippet", ""),
                            "url": result.get("url", ""),
                            "step": query_str,
                        }
                    )

        if not research_data:
            logger.warning("[Researcher] No research data gathered; using query as fallback")
            research_data.append(
                {
                    "source_type": "fallback",
                    "title": "Query Context",
                    "content": (
                        f"No external sources were retrieved for this request. "
                        f"Answer the user's question directly using general knowledge, "
                        f"and clearly avoid claiming external source verification. "
                        f"User question: {query}"
                    ),
                    "url": None,
                }
            )

        logger.info(f"[Researcher] Collected {len(research_data)} data points")

        return {
            **state,
            "research_data": research_data,
            "agent_status": "researched",
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "researcher",
                    "status": "completed",
                    "output": (
                        f"Collected {len(research_data)} sources: "
                        f"{sum(1 for d in research_data if d['source_type']=='web')} web, "
                        f"{sum(1 for d in research_data if d['source_type']=='arxiv')} arxiv, "
                        f"{sum(1 for d in research_data if d['source_type']=='rag')} rag"
                    ),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

    except Exception as e:
        logger.error(f"[Researcher] Error during research: {e}")
        return {
            **state,
            "research_data": research_data,
            "agent_status": "research_error",
            "error": str(e),
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "researcher",
                    "status": "error",
                    "output": f"Research error: {e}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }
