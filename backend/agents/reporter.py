"""
Reporter Agent.
LangGraph node that uses Gemini to generate a structured markdown research report.
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

REPORTER_SYSTEM_PROMPT = """You are an expert research report writer. Your job is to synthesize all research findings into a comprehensive, well-structured report.

The report must include:
1. A compelling title
2. Executive Summary (2-3 paragraphs)
3. Key Findings (detailed bullet points with explanations)
4. Key Concepts (definitions and explanations of important terms)
5. References (formatted citations from the research sources)
6. Conclusion (3-4 sentences with actionable insights)

Respond ONLY with valid JSON in this exact format:
{
    "title": "Research Report: [Topic]",
    "executive_summary": "Multi-paragraph executive summary...",
    "findings": ["Detailed finding 1", "Detailed finding 2", ...],
    "key_concepts": ["Concept 1: definition", "Concept 2: definition", ...],
    "references": [
        {"title": "Source title", "url": "https://...", "source": "web|arxiv|rag"},
        ...
    ],
    "conclusion": "Conclusion paragraph with actionable insights...",
    "markdown_report": "# Full Report Title\n\n## Executive Summary\n..."
}

Make the report professional, thorough, and actionable."""


def _build_full_context(state: Dict[str, Any], max_chars: int = 10000) -> str:
    """
    Build comprehensive context from all previous agent outputs for report generation.

    Args:
        state: The full workflow state.
        max_chars: Maximum characters for the context string.

    Returns:
        Formatted context string.
    """
    parts = []

    query = state.get("query", "")
    plan = state.get("plan", [])
    verified_facts = state.get("verified_facts", [])
    fact_check_notes = state.get("fact_check_notes", "")
    summary = state.get("summary", "")
    key_concepts = state.get("key_concepts", [])
    research_data = state.get("research_data", [])

    parts.append(f"RESEARCH QUERY: {query}\n")

    if plan:
        formatted_plan = []
        for s in plan:
            if isinstance(s, dict):
                formatted_plan.append(f"- [{s.get('source', 'web').upper()}] {s.get('query', '')}")
            else:
                formatted_plan.append(f"- {s}")
        parts.append(f"\nRESEARCH PLAN:\n" + "\n".join(formatted_plan))

    if summary:
        parts.append(f"\nSUMMARY:\n{summary[:2000]}")

    if verified_facts:
        facts_text = "\n".join(f"- {f}" for f in verified_facts[:20])
        parts.append(f"\nVERIFIED FACTS:\n{facts_text}")

    if key_concepts:
        parts.append(f"\nKEY CONCEPTS: {', '.join(key_concepts)}")

    if fact_check_notes:
        parts.append(f"\nFACT CHECK NOTES: {fact_check_notes[:500]}")

    # Add source URLs for references
    sources_section = []
    for item in research_data[:10]:
        title = item.get("title", "Untitled")
        url = item.get("url", "")
        source_type = item.get("source_type", "unknown")
        if title and (url or source_type == "rag"):
            sources_section.append(f"- [{source_type.upper()}] {title}: {url or 'local document'}")

    if sources_section:
        parts.append("\nSOURCES:\n" + "\n".join(sources_section))

    full_context = "\n".join(parts)
    return full_context[:max_chars]


def reporter_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph reporter node. Generates a structured research report using Gemini.

    Args:
        state: Complete workflow state with all previous agent outputs.

    Returns:
        Updated state with 'report' dict containing the full structured report.
    """
    query = state.get("query", "")

    logger.info(f"[Reporter] Generating research report for: '{query[:80]}'")
    state["agent_status"] = "reporting"

    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.REPORTER_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.5,
        )

        full_context = _build_full_context(state)

        messages = [
            SystemMessage(content=REPORTER_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Generate a comprehensive research report based on the following research:\n\n"
                    f"{full_context}"
                )
            ),
        ]

        response = llm.invoke(messages)
        result = loads_json_response(response.content)

        report = {
            "title": result.get("title", f"Research Report: {query}"),
            "executive_summary": result.get("executive_summary", ""),
            "findings": result.get("findings", []),
            "key_concepts": result.get("key_concepts", state.get("key_concepts", [])),
            "references": result.get("references", []),
            "conclusion": result.get("conclusion", ""),
            "markdown_report": result.get("markdown_report", ""),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        # If no markdown_report, build one
        if not report["markdown_report"]:
            report["markdown_report"] = _build_markdown_report(report)

        logger.info(f"[Reporter] Report generated: '{report['title']}'")

        return {
            **state,
            "report": report,
            "agent_status": "completed",
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "reporter",
                    "status": "completed",
                    "output": f"Report generated: '{report['title']}' with {len(report['findings'])} findings",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

    except JSONDecodeError as e:
        logger.error(f"[Reporter] JSON parse error: {e}")
        # Build a fallback report from state data
        fallback_report = _build_fallback_report(state)
        return {
            **state,
            "report": fallback_report,
            "agent_status": "completed_fallback",
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "reporter",
                    "status": "completed_with_fallback",
                    "output": "Fallback report generated due to parsing error",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

    except Exception as e:
        logger.error(f"[Reporter] Unexpected error: {e}")
        fallback_report = _build_fallback_report(state)
        return {
            **state,
            "report": fallback_report,
            "agent_status": "report_error",
            "error": str(e),
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "reporter",
                    "status": "error",
                    "output": f"Error: {e}. Fallback report generated.",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }


def _build_markdown_report(report: Dict[str, Any]) -> str:
    """
    Build a markdown report string from the structured report dict.

    Args:
        report: The structured report dictionary.

    Returns:
        Markdown formatted report string.
    """
    lines = [
        f"# {report.get('title', 'Research Report')}",
        "",
        "## Executive Summary",
        "",
        report.get("executive_summary", ""),
        "",
        "## Key Findings",
        "",
    ]

    for finding in report.get("findings", []):
        lines.append(f"- {finding}")

    lines.extend(["", "## Key Concepts", ""])
    for concept in report.get("key_concepts", []):
        lines.append(f"- {concept}")

    lines.extend(["", "## References", ""])
    for ref in report.get("references", []):
        title = ref.get("title", "Reference")
        url = ref.get("url", "")
        if url:
            lines.append(f"- [{title}]({url})")
        else:
            lines.append(f"- {title}")

    lines.extend(["", "## Conclusion", "", report.get("conclusion", ""), ""])

    return "\n".join(lines)


def _build_fallback_report(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a basic fallback report from the workflow state when LLM generation fails.

    Args:
        state: The workflow state.

    Returns:
        A basic report dict.
    """
    query = state.get("query", "Research Query")
    verified_facts = state.get("verified_facts", [])
    summary = state.get("summary", "No summary available.")
    key_concepts = state.get("key_concepts", [])
    research_data = state.get("research_data", [])

    references = [
        {
            "title": item.get("title", "Source"),
            "url": item.get("url", ""),
            "source": item.get("source_type", "unknown"),
        }
        for item in research_data
        if item.get("title") and item.get("url")
    ][:10]

    report = {
        "title": f"Research Report: {query}",
        "executive_summary": summary[:500] if summary else f"Research findings for: {query}",
        "findings": [f[:200] for f in verified_facts[:10]] if verified_facts else [f"Research on: {query}"],
        "key_concepts": key_concepts[:10],
        "references": references,
        "conclusion": f"This report summarizes research findings related to: {query}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    report["markdown_report"] = _build_markdown_report(report)
    return report
