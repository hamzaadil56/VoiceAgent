"""Configuration settings for VoiceAgent."""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Keys
    groq_api_key: str = Field(..., description="Groq API key")

    # LM Studio Configuration
    lm_studio_url: str = Field(
        default="http://localhost:1234/v1", description="LM Studio server URL"
    )
    tts_voice: str = Field(
        default="tara",
        description="Orpheus TTS voice (tara, leah, jess, leo, dan, mia, zac, zoe)",
    )

    # Model Configuration
    stt_model: str = Field(default="whisper-large-v3",
                           description="Speech-to-text model (Groq)")
    llm_model: str = Field(default="llama-3.3-70b-versatile",
                           description="LLM model for agent (Groq)")

    # Audio Configuration
    sample_rate: int = Field(
        default=16000, description="Audio sample rate in Hz")
    channels: int = Field(default=1, description="Number of audio channels")
    chunk_size: int = Field(
        default=1024, description="Audio chunk size for recording")
    record_seconds: int = Field(
        default=5, description="Maximum recording duration")
    silence_threshold: int = Field(
        default=500, description="Silence detection threshold")
    silence_duration: float = Field(
        default=2.0, description="Duration of silence to stop recording")

    # Agent Configuration
    agent_name: str = Field(default="VoiceAssistant", description="Agent name")
    agent_instructions: str = Field(
        default="You are a helpful voice assistant. Keep your responses concise and natural for spoken conversation.",
        description="Agent instructions",
    )
    max_tokens: int = Field(
        default=500, description="Maximum tokens for LLM response")
    temperature: float = Field(
        default=0.7, description="Temperature for LLM sampling")

    def __repr__(self) -> str:
        """String representation with masked API keys."""
        return (
            f"Settings("
            f"groq_api_key={'***' if self.groq_api_key else None}, "
            f"stt_model={self.stt_model}, "
            f"tts_voice={self.tts_voice}, "
            f"llm_model={self.llm_model})"
        )
