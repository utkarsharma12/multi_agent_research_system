"""
Configuration settings for the Multi-Agent Research System backend.
Loads environment variables from .env file using pydantic-settings pattern.
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)

DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


class Settings:
    """Application settings loaded from environment variables."""

    # Google Gemini API Models
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = DEFAULT_GEMINI_MODEL
    
    # Agent-Specific Models
    PLANNER_MODEL: str = os.getenv("PLANNER_MODEL", DEFAULT_GEMINI_MODEL)
    FACT_CHECKER_MODEL: str = os.getenv("FACT_CHECKER_MODEL", DEFAULT_GEMINI_MODEL)
    SUMMARIZER_MODEL: str = os.getenv("SUMMARIZER_MODEL", DEFAULT_GEMINI_MODEL)
    REPORTER_MODEL: str = os.getenv("REPORTER_MODEL", DEFAULT_GEMINI_MODEL)

    # ChromaDB
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./research.db")

    # CORS
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

    # File Upload
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))

    # Text chunking
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))

    # RAG
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "research_docs")
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))


settings = Settings()
