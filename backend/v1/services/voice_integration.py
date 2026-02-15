"""Session-aware voice integration service.

Bridges the VoiceService (STT/TTS) with the flow engine for session-bound
voice interactions. Each session gets its own processing context.
"""

from __future__ import annotations

import base64
import logging
from typing import AsyncIterator, Optional

from sqlalchemy.orm import Session

from ..models import RespondentSession
from ..services.flow_engine import FlowResult, process_user_message, start_session_prompt

logger = logging.getLogger(__name__)


class SessionVoiceProcessor:
    """Processes voice turns for a specific respondent session.

    Flow:
    1. STT: audio bytes -> transcript text
    2. Flow engine: transcript -> validation + next prompt
    3. TTS: prompt text -> PCM audio stream
    """

    def __init__(self, voice_service, db: Session, respondent_session: RespondentSession):
        self.voice_service = voice_service
        self.db = db
        self.respondent_session = respondent_session

    async def get_initial_prompt_audio(self) -> tuple[str, AsyncIterator[bytes]]:
        """Get the initial form prompt as text and audio stream."""
        prompt = start_session_prompt(self.db, self.respondent_session)

        async def empty_iter():
            return
            yield  # makes this an async generator  # noqa: E501

        if not self.voice_service:
            return prompt, empty_iter()

        try:
            _, audio_iter = await self.voice_service.process_text_message(prompt)
            return prompt, audio_iter
        except Exception as exc:
            logger.warning("Failed to synthesize initial prompt audio: %s", exc)
            return prompt, empty_iter()

    async def process_audio_turn(self, audio_bytes: bytes) -> tuple[str, FlowResult, Optional[AsyncIterator[bytes]]]:
        """Process a complete voice turn:
        1. STT on the audio
        2. Run through flow engine
        3. Synthesize response

        Returns: (transcript, flow_result, audio_response_iterator)
        """
        # Step 1: STT
        transcript = ""
        if self.voice_service and audio_bytes:
            try:
                transcript, _ = await self.voice_service.process_audio_chunk(audio_bytes)
            except Exception as exc:
                logger.error("STT failed: %s", exc)
                raise RuntimeError(f"Speech recognition failed: {exc}") from exc

        if not transcript.strip():
            transcript = "[voice-input-received]"

        # Step 2: Flow engine
        result = process_user_message(self.db, self.respondent_session, transcript)
        self.db.commit()

        # Step 3: TTS on assistant response
        audio_iter = None
        if self.voice_service and result.get("assistant_message"):
            try:
                _, audio_iter = await self.voice_service.process_text_message(
                    result["assistant_message"]
                )
            except Exception as exc:
                logger.warning("TTS failed: %s", exc)

        return transcript, result, audio_iter

    async def process_text_turn(self, text: str) -> tuple[FlowResult, Optional[AsyncIterator[bytes]]]:
        """Process a text-based turn with optional TTS response.

        Returns: (flow_result, audio_response_iterator)
        """
        result = process_user_message(self.db, self.respondent_session, text)
        self.db.commit()

        audio_iter = None
        if self.voice_service and result.get("assistant_message"):
            try:
                _, audio_iter = await self.voice_service.process_text_message(
                    result["assistant_message"]
                )
            except Exception as exc:
                logger.warning("TTS failed for text turn: %s", exc)

        return result, audio_iter


async def stream_audio_to_ws(websocket, audio_iter: AsyncIterator[bytes]) -> None:
    """Helper to stream PCM audio chunks over WebSocket as base64."""
    if audio_iter is None:
        return

    try:
        async for pcm_chunk in audio_iter:
            encoded = base64.b64encode(pcm_chunk).decode("ascii")
            await websocket.send_json({"type": "audio_chunk", "data": encoded})
        await websocket.send_json({"type": "audio_end"})
    except Exception as exc:
        logger.warning("Audio streaming error: %s", exc)
