"""
Chat API Routes.
Endpoints for running research workflows and managing chat history.
"""

import json
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Chat, Report
from database.schemas import (
    ChatRequest,
    ChatResponse,
    ChatListItem,
    DeleteResponse,
)
from graph.workflow import run_workflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    Run the multi-agent research workflow for a given query.

    Executes the full LangGraph pipeline (planner -> researcher -> fact_checker
    -> summarizer -> reporter), saves the result to the database, and returns
    the complete chat record including agent steps.

    Args:
        request: ChatRequest containing the research query.
        db: SQLAlchemy database session.

    Returns:
        ChatResponse with the full research result and agent execution steps.

    Raises:
        HTTPException 400: If the query is empty.
        HTTPException 500: If the workflow fails unexpectedly.
    """
    query = request.query.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty",
        )

    logger.info(f"[Chat API] Starting research for query: '{query[:100]}'")

    try:
        # Run the agent workflow
        result = await run_workflow(query)

        # Extract the report text as the main response
        report = result.get("report", {})
        response_text = report.get("markdown_report") or report.get("executive_summary") or result.get("summary", "")

        if not response_text:
            response_text = f"Research completed for: {query}"

        # Save to database
        chat = Chat(
            query=query,
            response=response_text,
            agent_steps=result.get("agent_steps", []),
        )
        db.add(chat)
        db.flush()  # Get the chat ID before committing

        # Save the report if one was generated
        if report and report.get("title"):
            db_report = Report(
                chat_id=chat.id,
                title=report.get("title", f"Report: {query[:100]}"),
                executive_summary=report.get("executive_summary", ""),
                findings=report.get("findings", []),
                references=report.get("references", []),
                conclusion=report.get("conclusion", ""),
            )
            db.add(db_report)

        db.commit()
        db.refresh(chat)

        logger.info(f"[Chat API] Research completed and saved with chat_id={chat.id}")

        return ChatResponse(
            id=chat.id,
            query=chat.query,
            response=chat.response,
            agent_steps=chat.agent_steps,
            report=report if report else None,
            created_at=chat.created_at,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"[Chat API] Workflow error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research workflow failed: {str(e)}",
        )


@router.get("/history", response_model=List[ChatListItem])
async def get_chat_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> List[ChatListItem]:
    """
    Retrieve paginated chat history.

    Args:
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return (max 100).
        db: SQLAlchemy database session.

    Returns:
        List of ChatListItem records ordered by most recent first.
    """
    limit = min(limit, 100)  # Cap at 100

    chats = (
        db.query(Chat)
        .order_by(Chat.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        ChatListItem(
            id=chat.id,
            query=chat.query,
            response=chat.response,
            created_at=chat.created_at,
        )
        for chat in chats
    ]


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: int,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    Retrieve a single chat session by ID.

    Args:
        chat_id: The unique ID of the chat record.
        db: SQLAlchemy database session.

    Returns:
        Full ChatResponse including agent steps.

    Raises:
        HTTPException 404: If the chat is not found.
    """
    chat = db.query(Chat).filter(Chat.id == chat_id).first()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat with id={chat_id} not found",
        )

    return ChatResponse(
        id=chat.id,
        query=chat.query,
        response=chat.response,
        agent_steps=chat.agent_steps,
        created_at=chat.created_at,
    )


@router.delete("/{chat_id}", response_model=DeleteResponse)
async def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
) -> DeleteResponse:
    """
    Delete a chat session by ID.

    Args:
        chat_id: The ID of the chat to delete.
        db: SQLAlchemy database session.

    Returns:
        DeleteResponse confirming deletion.

    Raises:
        HTTPException 404: If the chat is not found.
    """
    chat = db.query(Chat).filter(Chat.id == chat_id).first()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat with id={chat_id} not found",
        )

    db.delete(chat)
    db.commit()

    logger.info(f"[Chat API] Deleted chat_id={chat_id}")
    return DeleteResponse(message="Chat deleted successfully", id=chat_id)
