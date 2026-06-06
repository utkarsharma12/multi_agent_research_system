"""
Multi-Agent Research System — FastAPI Application Entry Point.

Configures the FastAPI app with CORS middleware, routes, startup/shutdown events,
and initializes the database and vector store on startup.
"""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database.connection import create_tables
from database.schemas import HealthResponse
from rag.vector_store import init_vector_store
from api.routes.chat import router as chat_router
from api.routes.documents import router as documents_router
from api.routes.reports import router as reports_router

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Multi-Agent Research System",
    description=(
        "A production-grade research system powered by LangGraph and Google Gemini. "
        "Orchestrates multiple AI agents to plan, research, fact-check, summarize, "
        "and report on any research topic."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ---------------------------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------------------------

# Allow all origins in development; restrict in production via CORS_ORIGINS env var
cors_origins = settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Startup & Shutdown Events
# ---------------------------------------------------------------------------


@app.on_event("startup")
async def on_startup() -> None:
    """
    Application startup handler.

    Performs the following initialization steps:
    1. Creates required directories (uploads, chroma_db)
    2. Creates all database tables
    3. Initializes the ChromaDB vector store collection
    """
    logger.info("=" * 60)
    logger.info("  Multi-Agent Research System — Starting Up")
    logger.info("=" * 60)

    # Ensure required directories exist
    for directory in [settings.UPLOAD_DIR, settings.CHROMA_PERSIST_DIR]:
        abs_dir = os.path.abspath(directory)
        os.makedirs(abs_dir, exist_ok=True)
        logger.info(f"  Directory ready: {abs_dir}")

    # Initialize database tables
    try:
        create_tables()
        logger.info("  Database tables created/verified ✓")
    except Exception as e:
        logger.error(f"  Database initialization failed: {e}")
        raise

    # Initialize ChromaDB vector store
    try:
        init_vector_store()
        logger.info("  ChromaDB vector store initialized ✓")
    except Exception as e:
        logger.error(f"  ChromaDB initialization failed: {e}")
        raise

    logger.info("=" * 60)
    logger.info("  Application startup complete — Ready to serve requests")
    logger.info(f"  Gemini Model: {settings.GEMINI_MODEL}")
    logger.info(f"  API Docs: http://localhost:8000/docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """
    Application shutdown handler.
    Logs a clean shutdown message.
    """
    logger.info("Multi-Agent Research System — Shutting down gracefully")


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(reports_router)


# ---------------------------------------------------------------------------
# Root / Health Endpoints
# ---------------------------------------------------------------------------


@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root() -> HealthResponse:
    """
    Root health check endpoint.

    Returns:
        HealthResponse with status 'ok' and application name.
    """
    return HealthResponse(
        status="ok",
        message="Multi-Agent Research System",
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """
    Detailed health check endpoint.

    Returns:
        HealthResponse indicating the system is operational.
    """
    return HealthResponse(
        status="ok",
        message="Multi-Agent Research System is running",
    )


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------


@app.exception_handler(404)
async def not_found_handler(request, exc) -> JSONResponse:
    """Handle 404 not found errors with a JSON response."""
    return JSONResponse(
        status_code=404,
        content={"detail": "The requested resource was not found"},
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc) -> JSONResponse:
    """Handle unexpected 500 errors with a JSON response."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"},
    )


# ---------------------------------------------------------------------------
# Development Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
