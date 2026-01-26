"""REST API routes for configuration and health checks."""

from fastapi import APIRouter, HTTPException
from backend.services.voice_service import VoiceService
from backend.config import BackendSettings
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
settings = BackendSettings()

# Global voice service instance (will be initialized in main.py)
voice_service: Optional[VoiceService] = None


class SettingsUpdate(BaseModel):
    """Settings update model."""

    agent_name: Optional[str] = None
    tts_voice: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    agent_instructions: Optional[str] = None
    max_turns: Optional[int] = None


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "voice-agent-api",
    }


@router.get("/settings")
async def get_settings():
    """Get current agent settings."""
    if not voice_service:
        raise HTTPException(
            status_code=503, detail="Voice service not initialized")
    return voice_service.get_settings()


@router.put("/settings")
async def update_settings(settings_update: SettingsUpdate):
    """Update agent settings."""
    if not voice_service:
        raise HTTPException(
            status_code=503, detail="Voice service not initialized")

    update_dict = settings_update.model_dump(exclude_unset=True)
    voice_service.update_settings(**update_dict)

    return {"status": "updated", "settings": voice_service.get_settings()}


@router.get("/voices")
async def get_voices():
    """Get available TTS voices."""
    if not voice_service:
        raise HTTPException(
            status_code=503, detail="Voice service not initialized")
    return {"voices": voice_service.get_available_voices()}
