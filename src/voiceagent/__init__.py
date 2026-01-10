"""
VoiceAgent - Production-grade voice agent using OpenAI Agents SDK and Groq models.
"""

__version__ = "0.1.0"

from .core.voice_agent import VoiceAgent
from .config.settings import Settings

__all__ = ["VoiceAgent", "Settings"]

