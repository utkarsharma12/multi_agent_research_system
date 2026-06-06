"""Shared helpers for handling LLM responses."""

import json
from typing import Any


def response_content_to_text(content: Any) -> str:
    """Normalize LangChain/Gemini content into plain text."""
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if text:
                    parts.append(str(text))
            else:
                text = getattr(item, "text", None) or getattr(item, "content", None)
                if text:
                    parts.append(str(text))
        return "\n".join(parts).strip()

    return str(content).strip()


def strip_json_fences(text: str) -> str:
    """Remove markdown code fences around a JSON response if present."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(line for line in lines if not line.startswith("```"))
    return text.strip()


def loads_json_response(content: Any) -> Any:
    """Parse a model response that should contain JSON."""
    return json.loads(strip_json_fences(response_content_to_text(content)))
