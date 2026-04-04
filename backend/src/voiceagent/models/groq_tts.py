"""Text-to-speech using Groq's OpenAI-compatible `/v1/audio/speech` API.

Supports PlayAI (`playai-tts`) and Orpheus (`canopylabs/orpheus-*`) models.
Groq returns WAV; we extract raw int16 PCM at 24 kHz for the Agents SDK and WebSocket clients.
"""

from __future__ import annotations

import io
import logging
import os
import wave
from typing import AsyncIterator

import httpx
import numpy as np

from agents.voice import TTSModel, TTSModelSettings

logger = logging.getLogger(__name__)

# Groq PlayAI TTS voices (see Groq docs)
DEFAULT_PLAYAI_VOICE = "Fritz-PlayAI"
PLAYAI_VOICES = frozenset(
    {
        "Arista-PlayAI",
        "Atlas-PlayAI",
        "Basil-PlayAI",
        "Briggs-PlayAI",
        "Calum-PlayAI",
        "Celeste-PlayAI",
        "Cheyenne-PlayAI",
        "Chip-PlayAI",
        "Cillian-PlayAI",
        "Deedee-PlayAI",
        "Fritz-PlayAI",
        "Gail-PlayAI",
        "Indigo-PlayAI",
        "Mamaw-PlayAI",
        "Mason-PlayAI",
        "Mikail-PlayAI",
        "Mitch-PlayAI",
        "Quinn-PlayAI",
        "Thunder-PlayAI",
        "Ahmad-PlayAI",
        "Amira-PlayAI",
        "Khalid-PlayAI",
        "Nasser-PlayAI",
    }
)

# Orpheus (canopylabs/orpheus-v1-english, canopylabs/orpheus-arabic-saudi)
DEFAULT_ORPHEUS_VOICE = "troy"
ORPHEUS_VOICES = frozenset(
    {
        "autumn",
        "diana",
        "hannah",
        "austin",
        "daniel",
        "troy",
        "fahad",
        "sultan",
        "lulwa",
        "noura",
    }
)

ORPHEUS_MAX_INPUT_CHARS = 200
TARGET_SAMPLE_RATE = 24000


def _is_orpheus_model(model: str) -> bool:
    m = (model or "").strip().lower()
    return "orpheus" in m or m.startswith("canopylabs/")


def _resolve_voice(model: str, voice: str) -> str:
    v = (voice or "").strip()
    if _is_orpheus_model(model):
        return v.lower() if v.lower() in ORPHEUS_VOICES else DEFAULT_ORPHEUS_VOICE
    return v if v in PLAYAI_VOICES else DEFAULT_PLAYAI_VOICE


def _chunk_text_for_orpheus(text: str, max_len: int = ORPHEUS_MAX_INPUT_CHARS) -> list[str]:
    """Split long text into chunks <= max_len, preferring sentence boundaries."""
    text = (text or "").strip()
    if not text:
        return []
    if len(text) <= max_len:
        return [text]

    chunks: list[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= max_len:
            chunks.append(remaining.strip())
            break
        window = remaining[: max_len + 1]
        # Prefer break after sentence end
        break_at = -1
        for sep in (". ", "? ", "! ", "\n"):
            idx = window.rfind(sep)
            if idx != -1 and idx + len(sep) <= max_len:
                break_at = idx + len(sep)
        if break_at == -1:
            # Last space before max_len
            space = window.rfind(" ", 0, max_len)
            break_at = space if space > 0 else max_len
        piece = remaining[:break_at].strip()
        if piece:
            chunks.append(piece)
        remaining = remaining[break_at:].lstrip()
    return [c for c in chunks if c]


def _wav_bytes_to_pcm_int16_mono_24k(wav_bytes: bytes) -> bytes:
    """Parse WAV bytes; return raw int16 mono PCM at 24 kHz."""
    bio = io.BytesIO(wav_bytes)
    with wave.open(bio, "rb") as wf:
        n_channels = wf.getnchannels()
        sample_rate = wf.getframerate()
        sampwidth = wf.getsampwidth()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    if sampwidth != 2:
        raise ValueError(f"Expected 16-bit WAV, got sampwidth={sampwidth}")

    audio = np.frombuffer(raw, dtype=np.int16)
    if n_channels > 1:
        audio = audio.reshape(-1, n_channels)[:, 0]

    if sample_rate != TARGET_SAMPLE_RATE:
        from scipy import signal

        num_samples = int(len(audio) * TARGET_SAMPLE_RATE / sample_rate)
        audio = signal.resample(audio.astype(np.float64), num_samples).astype(np.int16)

    return audio.tobytes()


class GroqTTSModel(TTSModel):
    """TTS via Groq `/v1/audio/speech` (PlayAI or Orpheus). Yields raw int16 PCM at 24 kHz."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        model: str = "canopylabs/orpheus-v1-english",
        voice: str = DEFAULT_ORPHEUS_VOICE,
        base_url: str = "https://api.groq.com/openai/v1",
        timeout: float = 120.0,
    ):
        self._api_key = (api_key or os.getenv("GROQ_API_KEY", "")).strip()
        if not self._api_key:
            raise ValueError("GROQ_API_KEY is required for GroqTTSModel")
        self._model = model.strip() if model else "playai-tts"
        self._voice = _resolve_voice(self._model, voice)
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @property
    def model_name(self) -> str:
        return self._model

    async def _speech_request(self, client: httpx.AsyncClient, input_text: str) -> bytes:
        payload: dict = {
            "model": self._model,
            "input": input_text,
            "voice": self._voice,
            "response_format": "wav",
        }
        logger.debug(
            "Groq TTS request: model=%s voice=%s input_len=%d",
            self._model,
            self._voice,
            len(input_text),
        )
        response = await client.post(
            f"{self._base_url}/audio/speech",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        if response.is_error:
            try:
                body = response.json()
            except Exception:
                body = response.text
            logger.error(
                "Groq TTS API error %d: model=%s voice=%s | response body: %s",
                response.status_code,
                self._model,
                self._voice,
                body,
            )
            response.raise_for_status()
        return response.content

    async def run(self, text: str, settings: TTSModelSettings) -> AsyncIterator[bytes]:
        if not (text or "").strip():
            return

        if _is_orpheus_model(self._model):
            segments = _chunk_text_for_orpheus(text.strip())
        else:
            segments = [text.strip()]

        chunk_size = 4096
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for segment in segments:
                if not segment:
                    continue
                try:
                    wav_data = await self._speech_request(client, segment)
                    pcm = _wav_bytes_to_pcm_int16_mono_24k(wav_data)
                except Exception:
                    logger.exception(
                        "GroqTTSModel failed for segment (model=%s voice=%s len=%d): %r…",
                        self._model,
                        self._voice,
                        len(segment),
                        segment[:80],
                    )
                    raise
                for i in range(0, len(pcm), chunk_size):
                    yield pcm[i : i + chunk_size]


def all_supported_voices_for_model(model: str) -> frozenset[str]:
    """Return voice IDs valid for the given Groq TTS model id."""
    if _is_orpheus_model(model):
        return ORPHEUS_VOICES
    return PLAYAI_VOICES
