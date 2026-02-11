"""FastAPI main application for Voice Agent web interface."""

import sys
from pathlib import Path

# Add backend/src so "voiceagent" resolves (voiceagent lives in backend/src/voiceagent/)
_backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_backend_dir / "src"))
# Add repo root so "backend" package resolves
sys.path.insert(0, str(_backend_dir.parent))

from fastapi import FastAPI, WebSocket, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.config import BackendSettings
from backend.logging_config import setup_logging, get_logger
from backend.routes import api
from backend.routes.websocket import websocket_endpoint
from backend.services.voice_service import VoiceService
from rich.console import Console
from contextlib import asynccontextmanager
import uvicorn

# Initialize settings first so we can use log_level
settings = BackendSettings()

# Set up logging so server errors are visible clearly (MemoryError, OSError, etc.)
setup_logging(level=settings.log_level)
logger = get_logger(__name__)
console = Console()

# Initialize voice service
voice_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    global voice_service

    # Startup
    try:
        logger.info("Initializing Voice Service...")
        voice_service = VoiceService()
        # Set global reference for routes
        api.voice_service = voice_service
        from backend.routes import websocket as ws_module
        ws_module.voice_service = voice_service
        logger.info("Voice Service ready")
    except Exception as e:
        logger.exception("Failed to initialize Voice Service: %s", e)
        raise

    yield

    # Shutdown
    logger.info("Shutting down Voice Agent API...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Voice Agent API",
    description="Web API for Voice Agent with WebSocket support",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch unhandled exceptions so the server stays alive and errors are logged."""
    logger.exception(
        "Unhandled exception: %s (path=%s)",
        exc,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__,
        },
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(api.router, prefix="/api", tags=["api"])

# WebSocket endpoint


@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    """WebSocket endpoint for voice communication."""
    await websocket_endpoint(websocket)


@app.get("/")
async def root():
    """Root endpoint."""
    return JSONResponse(
        {
            "service": "Voice Agent API",
            "version": "1.0.0",
            "status": "running",
            "websocket": "/ws",
            "api": "/api",
        }
    )


if __name__ == "__main__":
    logger.info("Starting Voice Agent API on %s:%s", settings.host, settings.port)
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info",
    )
