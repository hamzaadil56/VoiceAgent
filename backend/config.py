"""Backend configuration for FastAPI application."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class BackendSettings(BaseSettings):
    """Backend application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # CORS Configuration
    cors_origins: list[str] = ["http://localhost:5173",
                               "http://localhost:3000", "http://localhost:5174"]

    # WebSocket Configuration
    ws_max_connections: int = 100
    ws_timeout: int = 60

    # Audio Configuration
    audio_sample_rate: int = 24000
    audio_channels: int = 1
    audio_chunk_size: int = 4096

    # TTS spin endpoint auth (Bearer token)
    tts_api_key: str = ""
