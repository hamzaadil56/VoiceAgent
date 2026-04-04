"""REST API routes for configuration and health checks."""

import os
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.logging_config import get_logger
from backend.services.voice_service import VoiceService

router = APIRouter()
logger = get_logger(__name__)

# Global voice service instance (will be initialized in main.py)
voice_service: Optional[VoiceService] = None


class SettingsUpdate(BaseModel):
    """Settings update model."""

    agent_name: Optional[str] = None
    tts_voice: Optional[str] = None
    tts_model: Optional[str] = None
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
    Warm / verify Groq API connectivity (STT/LLM/TTS). Frontend can call this
    while showing 'Voice agent is getting ready'.
    """
    if not voice_service:
        raise HTTPException(
            status_code=503, detail="Voice service not initialized"
        )
    api_key = os.getenv("GROQ_API_KEY", "") or voice_service.settings.groq_api_key
    if not api_key:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY not configured")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            response.raise_for_status()
            data = response.json()
            return {"status": "ok", "groq": "reachable", "models_count": len(data.get("data", []))}
    except httpx.TimeoutException:
        logger.warning("Groq API did not respond in time")
        raise HTTPException(
            status_code=504,
            detail="Groq API did not respond in time",
        )
    except httpx.HTTPStatusError as e:
        logger.warning("Groq API error: %s %s", e.response.status_code, e.response.text)
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Groq API error: {e.response.text}",
        )
    except Exception as e:
        logger.exception("Failed to reach Groq API: %s", e)
        raise HTTPException(
            status_code=502,
            detail=f"Failed to reach Groq API: {str(e)}",
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
