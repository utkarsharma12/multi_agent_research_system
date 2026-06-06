"""
Planner Agent.
LangGraph node that uses Gemini to decompose a research query into actionable steps.
"""

import logging
from json import JSONDecodeError
from datetime import datetime, timezone
from typing import Any, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from agents.llm_utils import loads_json_response
from config import settings

logger = logging.getLogger(__name__)

# System prompt for the planning agent
PLANNER_SYSTEM_PROMPT = """You are an expert research planner. Your job is to break down a research query into 3-5 clear, actionable research steps.

Each step must specify the optimal search keywords and the exact database to use to avoid misunderstanding the context.
- "query": Must be concise, keyword-focused search string (NOT a full sentence). Use specific keywords to avoid misunderstanding the topic (e.g., add 'politics', 'biography', or 'history').
- "source": Must be either "web" (for general knowledge, news, people, history) or "arxiv" (strictly for math, physics, CS, academic research).

Respond ONLY with a valid JSON array of objects. No markdown, no explanation, just the JSON array.

Example output:
[
  {"query": "Narendra Modi biography early life", "source": "web"},
  {"query": "Narendra Modi major political policies Prime Minister", "source": "web"},
  {"query": "Narendra Modi economic reforms", "source": "web"}
]
"""


def planner_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph planner node. Breaks a user query into a structured research plan.

    Args:
        state: The current workflow state dict containing at least 'query'.

    Returns:
        Updated state dict with 'plan' (list of steps) and 'current_step' index set to 0.
    """
    query = state.get("query", "")
    logger.info(f"[Planner] Planning research for query: '{query[:80]}'")

    # Update agent status
    state["agent_status"] = "planning"

    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.PLANNER_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.3,
        )

        messages = [
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(
                content=f"Create a research plan for the following query:\n\n{query}"
            ),
        ]

        # Parse JSON plan
        response = llm.invoke(messages)
        plan = loads_json_response(response.content)

        if not isinstance(plan, list):
            raise ValueError("Planner response is not a JSON array")

        # Ensure we have 3-5 steps and they are valid dicts
        valid_plan = []
        for step in plan:
            if isinstance(step, dict) and "query" in step and "source" in step:
                valid_plan.append({"query": str(step["query"]).strip(), "source": str(step["source"]).strip()})
        
        plan = valid_plan[:5]
        if len(plan) < 1:
            raise ValueError("Planner returned empty or invalid steps")

        logger.info(f"[Planner] Generated {len(plan)} research steps")

        return {
            **state,
            "plan": plan,
            "current_step": 0,
            "agent_status": "planned",
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "planner",
                    "status": "completed",
                    "output": f"Created {len(plan)} research steps: " + "; ".join([s["query"] for s in plan]),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

    except JSONDecodeError as e:
        logger.error(f"[Planner] Failed to parse JSON response: {e}")
        # Fallback plan
        fallback_plan = [
            {"query": f"{query} background information", "source": "web"},
            {"query": f"{query} recent developments news", "source": "web"},
            {"query": f"{query} key concepts terminology", "source": "web"},
            {"query": f"{query} expert opinions analysis", "source": "web"},
        ]
        return {
            **state,
            "plan": fallback_plan,
            "current_step": 0,
            "agent_status": "planned_fallback",
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "planner",
                    "status": "completed_with_fallback",
                    "output": f"Used fallback plan with {len(fallback_plan)} steps",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }

    except Exception as e:
        logger.error(f"[Planner] Unexpected error: {e}")
        return {
            **state,
            "plan": [{"query": query, "source": "web"}],
            "current_step": 0,
            "agent_status": "planned_error",
            "error": str(e),
            "agent_steps": state.get("agent_steps", [])
            + [
                {
                    "agent": "planner",
                    "status": "error",
                    "output": f"Planning error: {e}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }
