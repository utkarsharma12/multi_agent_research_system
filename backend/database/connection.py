"""
Database connection module.
Sets up SQLAlchemy engine, session factory, declarative base, and FastAPI dependency.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from config import settings


# Create SQLAlchemy engine
# connect_args={"check_same_thread": False} is needed for SQLite
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a SQLAlchemy database session.
    Ensures the session is closed after the request completes.

    Yields:
        Session: SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """
    Create all database tables defined by ORM models.
    Should be called on application startup.
    """
    # Import models to ensure they are registered with the Base metadata
    from database import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
