"""Custom STT model provider for Groq Whisper."""

import io
import wave
from typing import AsyncIterator
from groq import Groq
from agents.voice import STTModel, STTModelSettings, AudioInput, StreamedAudioInput, StreamedTranscriptionSession


class GroqSTTModel(STTModel):
    """Speech-to-text model using Groq's Whisper."""

    def __init__(self, api_key: str, model: str = "whisper-large-v3"):
        """
        Initialize Groq STT model.

        Args:
            api_key: Groq API key
            model: Whisper model to use
        """
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
        """
        Transcribe audio to text using Groq Whisper.

        Args:
            input: Audio input data
            settings: STT model settings
            trace_include_sensitive_data: Whether to include sensitive data in traces
            trace_include_sensitive_audio_data: Whether to include audio data in traces

        Returns:
            Transcribed text
        """
        # Convert audio buffer to WAV format
        audio_bytes = input.buffer.tobytes()

        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(24000)  # 24kHz (OpenAI Agents SDK standard)
            wf.writeframes(audio_bytes)

        wav_buffer.seek(0)
        wav_buffer.name = "audio.wav"

        # Call Groq Whisper API
        transcription = self.client.audio.transcriptions.create(
            file=wav_buffer,
            model=self.model,
            language=settings.language or "en",
            response_format="text",
        )

        # Return the transcribed text
        if isinstance(transcription, str):
            return transcription.strip()
        else:
            return transcription.text.strip()

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
