"""Custom STT model provider for Groq Whisper."""

import io
import logging
import wave

from groq import Groq
from agents.voice import STTModel, STTModelSettings, AudioInput, StreamedAudioInput, StreamedTranscriptionSession

logger = logging.getLogger(__name__)


class GroqSTTModel(STTModel):
    """Speech-to-text model using Groq's Whisper."""

    def __init__(self, api_key: str, model: str = "whisper-large-v3"):
        self.client = Groq(api_key=api_key)
        self.model = model

    @property
    def model_name(self) -> str:
        """Return the model name."""
        return self.model

    async def transcribe(
        self,
        input: AudioInput,
        settings: STTModelSettings,
        trace_include_sensitive_data: bool,
        trace_include_sensitive_audio_data: bool,
    ) -> str:
        audio_bytes = input.buffer.tobytes()

        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_bytes)

        wav_buffer.seek(0)
        wav_buffer.name = "audio.wav"

        transcription = self.client.audio.transcriptions.create(
            file=wav_buffer,
            model=self.model,
            language=settings.language or "en",
            response_format="text",
        )

        text = transcription.strip() if isinstance(transcription, str) else transcription.text.strip()
        logger.info("Whisper STT result: %r (audio_bytes=%d)", text, len(audio_bytes))
        return text

    async def create_session(
        self,
        input: StreamedAudioInput,
        settings: STTModelSettings,
        trace_include_sensitive_data: bool,
        trace_include_sensitive_audio_data: bool,
    ) -> StreamedTranscriptionSession:
        """
        Create a streamed transcription session.

        Note: Groq Whisper doesn't support streaming transcription, so this is not implemented.
        For streaming, you would need to use OpenAI's Realtime API or similar.

        Args:
            input: Streamed audio input
            settings: STT model settings
            trace_include_sensitive_data: Whether to include sensitive data in traces
            trace_include_sensitive_audio_data: Whether to include audio data in traces

        Returns:
            A transcription session

        Raises:
            NotImplementedError: Groq Whisper doesn't support streaming
        """
        raise NotImplementedError(
            "Groq Whisper does not support streaming transcription. "
            "Use non-streaming transcribe() method instead."
        )
