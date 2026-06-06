"""
Summarizer Agent.
LangGraph node that uses Gemini to create concise bullet-point summaries
and extract key concepts from verified research facts.
"""

import logging
from json import JSONDecodeError
from datetime import datetime, timezone
from typing import Any, Dict, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from agents.llm_utils import loads_json_response
from config import settings

logger = logging.getLogger(__name__)

SUMMARIZER_SYSTEM_PROMPT = """You are an expert research summarizer. Your job is to:
1. Create concise, informative bullet-point notes from the verified facts
2. Extract and list the key concepts and terms from the research
3. Organize information in a clear, readable format

Respond ONLY with valid JSON in this exact format:
{
    "summary": "Comprehensive summary paragraph (2-4 sentences)",
    "bullet_points": ["• Key finding 1", "• Key finding 2", ...],
    "key_concepts": ["concept1", "concept2", "concept3", ...]
}

Be thorough but concise. Focus on the most important and actionable insights."""


def summarizer_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph summarizer node. Creates structured summaries and extracts key concepts.

    Args:
        state: Workflow state containing 'query', 'verified_facts', and 'fact_check_notes'.

    Returns:
        Updated state with 'summary' (str) and 'key_concepts' (list of str).
    """
    query = state.get("query", "")
    verified_facts = state.get("verified_facts", [])
    fact_check_notes = state.get("fact_check_notes", "")

    logger.info(f"[Summarizer] Summarizing {len(verified_facts)} verified facts")
    state["agent_status"] = "summarizing"

    if not verified_facts:
        logger.warning("[Summarizer] No verified facts to summarize")
        return {
            **state,
            "summary": f"No verified information was found for the query: {query}",
            "key_concepts": [],
            "agent_status": "summarized",
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "summarizer",
                    "status": "skipped",
                    "output": "No facts to summarize",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.SUMMARIZER_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.4,
        )

        # Build facts context
        facts_text = "\n".join(f"- {fact}" for fact in verified_facts[:30])
        notes_section = f"\n\nFact-check notes: {fact_check_notes}" if fact_check_notes else ""

        messages = [
            SystemMessage(content=SUMMARIZER_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Research Query: {query}\n\n"
                    f"Verified Facts:\n{facts_text}"
                    f"{notes_section}"
                )
            ),
        ]

        response = llm.invoke(messages)
        result = loads_json_response(response.content)

        summary = result.get("summary", "")
        bullet_points = result.get("bullet_points", [])
        key_concepts = result.get("key_concepts", [])

        # Combine summary with bullet points for the full summary field
        full_summary = summary
        if bullet_points:
            full_summary += "\n\n" + "\n".join(bullet_points)

        logger.info(
            f"[Summarizer] Created summary ({len(full_summary)} chars), "
            f"{len(key_concepts)} key concepts"
        )

        return {
            **state,
            "summary": full_summary,
            "key_concepts": key_concepts,
            "agent_status": "summarized",
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "summarizer",
                    "status": "completed",
                    "output": (
                        f"Summary created ({len(full_summary)} chars). "
                        f"Key concepts: {', '.join(key_concepts[:5])}"
                    ),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

    except JSONDecodeError as e:
        logger.error(f"[Summarizer] JSON parse error: {e}")
        # Fallback: use raw facts as summary
        fallback_summary = f"Research findings for '{query}':\n\n" + "\n".join(
            f"• {fact}" for fact in verified_facts[:10]
        )
        return {
            **state,
            "summary": fallback_summary,
            "key_concepts": [],
            "agent_status": "summarized_fallback",
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "summarizer",
                    "status": "completed_with_fallback",
                    "output": "Used fallback summary from raw facts",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

    except Exception as e:
        logger.error(f"[Summarizer] Unexpected error: {e}")
        return {
            **state,
            "summary": f"Summarization failed for query: {query}. Error: {str(e)}",
            "key_concepts": [],
            "agent_status": "summarize_error",
            "error": str(e),
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "summarizer",
                    "status": "error",
                    "output": f"Error: {e}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }
