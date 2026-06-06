"""
Pydantic schemas for request/response validation in the Multi-Agent Research System.
Defines schemas for Chat, Document, and Report models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


NON_RESEARCH_INPUTS = {
    "hello",
    "hi",
    "hey",
    "hii",
    "hiii",
    "ok",
    "okay",
    "test",
    "thanks",
    "thank you",
}


# ---------------------------------------------------------------------------
# Chat Schemas
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    """Schema for a new research chat request."""

    query: str = Field(..., min_length=3, max_length=5000, description="The research query")

    @model_validator(mode="before")
    @classmethod
    def normalize_query_field(cls, data: Any) -> Any:
        """Accept common chat payload field names from different clients."""
        if isinstance(data, dict) and "query" not in data:
            for key in ("message", "prompt", "content"):
                if key in data:
                    return {**data, "query": data[key]}
        return data

    @field_validator("query")
    @classmethod
    def strip_query(cls, value: str) -> str:
        query = value.strip()
        if query.lower() in NON_RESEARCH_INPUTS:
            raise ValueError(
                "Please enter a specific research question, for example: "
                "'What are the latest applications of quantum computing?'"
            )
        return query


class AgentStep(BaseModel):
    """Represents a single step in the agent execution pipeline."""

    agent: str = Field(..., description="Name of the agent (planner, researcher, etc.)")
    status: str = Field(..., description="Status: running | completed | error")
    output: Optional[str] = Field(None, description="Summary output from the agent step")
    timestamp: Optional[str] = Field(None, description="ISO timestamp of execution")


class ChatResponse(BaseModel):
    """Schema for a completed research chat response."""

    id: int
    query: str
    response: Optional[str]
    agent_steps: Optional[List[Dict[str, Any]]]
    report: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatListItem(BaseModel):
    """Schema for a chat item in the history list."""

    id: int
    query: str
    response: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Document Schemas
# ---------------------------------------------------------------------------


class DocumentResponse(BaseModel):
    """Schema for a document record response."""

    id: int
    title: str
    source: Optional[str]
    file_path: Optional[str]
    embedding_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """Schema for the response after uploading and indexing a document."""

    message: str
    document: DocumentResponse
    chunks_indexed: int


# ---------------------------------------------------------------------------
# Report Schemas
# ---------------------------------------------------------------------------


class ReportCreate(BaseModel):
    """Schema for creating a new report (internal use)."""

    chat_id: Optional[int] = None
    title: str
    executive_summary: Optional[str] = None
    findings: Optional[List[str]] = None
    references: Optional[List[Dict[str, str]]] = None
    conclusion: Optional[str] = None


class ReportResponse(BaseModel):
    """Schema for a full report response."""

    id: int
    chat_id: Optional[int]
    title: str
    executive_summary: Optional[str]
    findings: Optional[List[Any]]
    references: Optional[List[Any]]
    conclusion: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ReportListItem(BaseModel):
    """Schema for a report item in the list view."""

    id: int
    chat_id: Optional[int]
    title: str
    executive_summary: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# General / Health
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    """Schema for the health check response."""

    status: str
    message: str


class DeleteResponse(BaseModel):
    """Schema for a generic delete operation response."""

    message: str
    id: int
