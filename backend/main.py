"""FastAPI main application for Voice Agent web interface."""

import sys
from pathlib import Path

# Add backend/src so "voiceagent" resolves (voiceagent lives in backend/src/voiceagent/)
_backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(_backend_dir / "src"))
# Add repo root so "backend" package resolves
sys.path.insert(0, str(_backend_dir.parent))

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.config import BackendSettings
from backend.routes import api
from backend.routes.websocket import websocket_endpoint
from backend.services.voice_service import VoiceService
from rich.console import Console
from contextlib import asynccontextmanager
import uvicorn


console = Console()

# Initialize settings
settings = BackendSettings()

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
        console.print("[bold blue]🚀 Initializing Voice Service...[/bold blue]")
        voice_service = VoiceService()
        # Set global reference for routes
        api.voice_service = voice_service
        from backend.routes import websocket as ws_module
        ws_module.voice_service = voice_service
        console.print("[bold green]✓ Voice Service ready![/bold green]")
    except Exception as e:
        console.print(
            f"[bold red]✗ Failed to initialize Voice Service: {e}[/bold red]")
        raise

    yield

    # Shutdown
    console.print("[yellow]Shutting down Voice Agent API...[/yellow]")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Voice Agent API",
    description="Web API for Voice Agent with WebSocket support",
    version="1.0.0",
    lifespan=lifespan,
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
    console.print(
        f"[bold cyan]Starting Voice Agent API on {settings.host}:{settings.port}[/bold cyan]")
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level="info",
    )
