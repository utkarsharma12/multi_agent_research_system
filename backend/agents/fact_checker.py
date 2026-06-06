"""
Fact Checker Agent.
LangGraph node that uses Gemini to verify research data, detect contradictions,
and rate source reliability.
"""

import json
import logging
from json import JSONDecodeError
from datetime import datetime, timezone
from typing import Any, Dict, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from agents.llm_utils import loads_json_response
from config import settings

logger = logging.getLogger(__name__)

FACT_CHECKER_SYSTEM_PROMPT = """You are a rigorous fact-checker and research analyst. Your job is to:
1. Cross-reference gathered research data to identify consistent facts
2. Detect contradictions or conflicting information between sources
3. Rate the reliability of sources (high/medium/low)
4. Extract verified, trustworthy facts

Respond ONLY with valid JSON in this exact format:
{
    "verified_facts": ["fact1", "fact2", ...],
    "contradictions": ["description of contradiction 1", ...],
    "source_reliability": {
        "web_sources": "high|medium|low",
        "arxiv_sources": "high|medium|low",
        "rag_sources": "high|medium|low"
    },
    "fact_check_notes": "Overall assessment of source quality and reliability"
}

Be thorough but concise. Focus on facts directly relevant to the research query."""


def _build_research_context(research_data: List[Dict[str, Any]], max_chars: int = 8000) -> str:
    """
    Build a condensed text representation of the research data for the LLM.

    Args:
        research_data: List of research source dicts.
        max_chars: Maximum total characters to include.

    Returns:
        Formatted string of research sources.
    """
    parts = []
    total_chars = 0

    for i, item in enumerate(research_data, start=1):
        source_type = item.get("source_type", "unknown").upper()
        title = item.get("title", "Untitled")
        content = item.get("content", "")
        url = item.get("url", "")

        entry = f"[Source {i} - {source_type}]\nTitle: {title}\n"
        if url:
            entry += f"URL: {url}\n"
        if content:
            # Truncate individual content to avoid token limits
            entry += f"Content: {content[:600]}\n"

        entry += "\n"

        if total_chars + len(entry) > max_chars:
            break

        parts.append(entry)
        total_chars += len(entry)

    return "".join(parts)


def _extract_fallback_facts(research_data: List[Dict[str, Any]]) -> List[str]:
    """Use source snippets as facts when LLM-based fact checking is unavailable."""
    facts = []
    for item in research_data[:8]:
        source_type = item.get("source_type", "source")

        title = item.get("title", "Source")
        content = item.get("content", "").strip()
        if content:
            prefix = "Context" if source_type == "fallback" else title
            facts.append(f"{prefix}: {content[:300]}")

    return facts


def fact_checker_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph fact-checker node. Verifies research data using Gemini.

    Args:
        state: Workflow state containing 'query' and 'research_data'.

    Returns:
        Updated state with 'verified_facts' (list) and 'fact_check_notes' (str).
    """
    query = state.get("query", "")
    research_data = state.get("research_data", [])

    logger.info(f"[FactChecker] Verifying {len(research_data)} research items")
    state["agent_status"] = "fact_checking"

    if not research_data:
        logger.warning("[FactChecker] No research data to verify")
        return {
            **state,
            "verified_facts": ["No research data available for verification"],
            "fact_check_notes": "No data was gathered during the research phase.",
            "agent_status": "fact_checked",
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "fact_checker",
                    "status": "skipped",
                    "output": "No research data available",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.FACT_CHECKER_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.1,
        )

        research_context = _build_research_context(research_data)

        messages = [
            SystemMessage(content=FACT_CHECKER_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Research Query: {query}\n\n"
                    f"Research Data to Verify:\n\n{research_context}"
                )
            ),
        ]

        response = llm.invoke(messages)
        result = loads_json_response(response.content)

        verified_facts = result.get("verified_facts", [])
        contradictions = result.get("contradictions", [])
        fact_check_notes = result.get("fact_check_notes", "")
        source_reliability = result.get("source_reliability", {})

        # Combine notes with contradiction info
        full_notes = fact_check_notes
        if contradictions:
            full_notes += f"\n\nContradictions found: {'; '.join(contradictions)}"
        if source_reliability:
            full_notes += f"\n\nSource reliability: {json.dumps(source_reliability)}"

        logger.info(
            f"[FactChecker] Verified {len(verified_facts)} facts, "
            f"found {len(contradictions)} contradictions"
        )

        return {
            **state,
            "verified_facts": verified_facts,
            "fact_check_notes": full_notes,
            "agent_status": "fact_checked",
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "fact_checker",
                    "status": "completed",
                    "output": (
                        f"Verified {len(verified_facts)} facts. "
                        f"Contradictions: {len(contradictions)}. "
                        f"{fact_check_notes[:200]}"
                    ),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

    except JSONDecodeError as e:
        logger.error(f"[FactChecker] JSON parse error: {e}")
        # Extract raw text as verified facts fallback
        verified_facts = _extract_fallback_facts(research_data)
        return {
            **state,
            "verified_facts": verified_facts,
            "fact_check_notes": "Fact checking completed with parsing issues. Using raw source content.",
            "agent_status": "fact_checked_fallback",
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "fact_checker",
                    "status": "completed_with_fallback",
                    "output": f"Used fallback fact extraction. {len(verified_facts)} items",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

    except Exception as e:
        logger.error(f"[FactChecker] Unexpected error: {e}")
        verified_facts = _extract_fallback_facts(research_data)
        if verified_facts:
            return {
                **state,
                "verified_facts": verified_facts,
                "fact_check_notes": (
                    f"Fact checking failed: {str(e)}. "
                    "Using gathered source snippets as unverified fallback facts."
                ),
                "agent_status": "fact_checked_fallback",
                "error": str(e),
                "agent_steps": state.get("agent_steps", [])
                + [
                    {
                        "agent": "fact_checker",
                        "status": "completed_with_fallback",
                        "output": f"Fact checking failed; used {len(verified_facts)} gathered source snippets.",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                ],
            }

        return {
            **state,
            "verified_facts": [],
            "fact_check_notes": f"Fact checking failed: {str(e)}",
            "agent_status": "fact_check_error",
            "error": str(e),
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "fact_checker",
                    "status": "error",
                    "output": f"Error: {e}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }
