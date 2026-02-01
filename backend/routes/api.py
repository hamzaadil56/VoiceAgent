"""REST API routes for configuration and health checks."""

import httpx
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


@router.get("/spin")
async def spin_server():
    """
    Wake the serverless TTS endpoint by calling its /ping.
    Backend sends Authorization: Bearer <TTS_API_KEY> from env. Returns the TTS
    service health response. Frontend can call this and show 'Voice agent is
    getting ready' while the request is pending.
    """
    if not voice_service:
        raise HTTPException(
            status_code=503, detail="Voice service not initialized"
        )
    base_url = voice_service.settings.lm_studio_url.rstrip("/")
    ping_url = f"{base_url}/ping"
    headers = {}
    if settings.tts_api_key:
        headers["Authorization"] = f"Bearer {settings.tts_api_key}"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(ping_url, headers=headers)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="TTS server did not respond in time (serverless may still be waking)",
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"TTS server error: {e.response.text}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to reach TTS server: {str(e)}",
        )


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
