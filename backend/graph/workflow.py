"""
LangGraph Workflow for the Multi-Agent Research System.
Defines the StateGraph with planner -> researcher -> fact_checker -> summarizer -> reporter pipeline.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import StateGraph, END

from agents.planner import planner_node
from agents.researcher import researcher_node
from agents.fact_checker import fact_checker_node
from agents.summarizer import summarizer_node
from agents.reporter import reporter_node

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# State Definition
# ---------------------------------------------------------------------------


class ResearchState(TypedDict, total=False):
    """
    TypedDict defining the shape of the LangGraph workflow state.
    All fields are optional to allow incremental updates across nodes.
    """

    # Input
    query: str

    # Planner outputs
    plan: List[Dict[str, str]]
    current_step: int

    # Researcher outputs
    research_data: List[Dict[str, Any]]

    # Fact checker outputs
    verified_facts: List[str]
    fact_check_notes: str

    # Summarizer outputs
    summary: str
    key_concepts: List[str]

    # Reporter outputs
    report: Dict[str, Any]

    # Orchestration metadata
    agent_status: str
    agent_steps: List[Dict[str, Any]]
    error: Optional[str]


# ---------------------------------------------------------------------------
# Graph Construction
# ---------------------------------------------------------------------------


def build_workflow() -> Any:
    """
    Build and compile the LangGraph StateGraph for the research pipeline.

    The pipeline flows linearly:
        planner -> researcher -> fact_checker -> summarizer -> reporter -> END

    Returns:
        Compiled LangGraph application (CompiledGraph).
    """
    workflow = StateGraph(ResearchState)

    # Register nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("fact_checker", fact_checker_node)
    workflow.add_node("summarizer", summarizer_node)
    workflow.add_node("reporter", reporter_node)

    # Set the entry point
    workflow.set_entry_point("planner")

    # Define linear edges
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "fact_checker")
    workflow.add_edge("fact_checker", "summarizer")
    workflow.add_edge("summarizer", "reporter")
    workflow.add_edge("reporter", END)

    compiled = workflow.compile()
    logger.info("LangGraph research workflow compiled successfully")
    return compiled


# Singleton compiled workflow
_workflow = None


def get_workflow() -> Any:
    """
    Get or create the singleton compiled LangGraph workflow.

    Returns:
        Compiled LangGraph workflow application.
    """
    global _workflow
    if _workflow is None:
        _workflow = build_workflow()
    return _workflow


async def run_workflow(query: str) -> Dict[str, Any]:
    """
    Execute the full multi-agent research workflow for a given query.

    Runs the LangGraph pipeline asynchronously by invoking it in a thread
    pool executor (since LangGraph's sync invoke is CPU/IO bound).

    Args:
        query: The research query string.

    Returns:
        Final workflow state dict containing all agent outputs including
        plan, research_data, verified_facts, summary, key_concepts, report,
        agent_steps, and agent_status.

    Raises:
        ValueError: If the query is empty.
        Exception: If the workflow encounters an unrecoverable error.
    """
    if not query or not query.strip():
        raise ValueError("Research query cannot be empty")

    logger.info(f"[Workflow] Starting research pipeline for query: '{query[:100]}'")

    # Initial state
    initial_state: ResearchState = {
        "query": query.strip(),
        "plan": [],
        "current_step": 0,
        "research_data": [],
        "verified_facts": [],
        "fact_check_notes": "",
        "summary": "",
        "key_concepts": [],
        "report": {},
        "agent_status": "initializing",
        "agent_steps": [
            {
                "agent": "workflow",
                "status": "started",
                "output": f"Research pipeline started for: {query[:100]}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ],
        "error": None,
    }

    workflow = get_workflow()

    try:
        # Run the synchronous LangGraph invoke in a thread pool to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        final_state = await loop.run_in_executor(
            None,
            lambda: workflow.invoke(initial_state),
        )

        logger.info(
            f"[Workflow] Pipeline completed. Status: {final_state.get('agent_status')}. "
            f"Steps: {len(final_state.get('agent_steps', []))}"
        )

        # Append completion step
        final_state["agent_steps"] = final_state.get("agent_steps", []) + [
            {
                "agent": "workflow",
                "status": "completed",
                "output": "Research pipeline completed successfully",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        ]

        return dict(final_state)

    except Exception as e:
        logger.error(f"[Workflow] Pipeline failed: {e}")
        return {
            **initial_state,
            "agent_status": "failed",
            "error": str(e),
            "agent_steps": initial_state.get("agent_steps", [])
            + [
                {
                    "agent": "workflow",
                    "status": "failed",
                    "output": f"Pipeline failed: {str(e)}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }
