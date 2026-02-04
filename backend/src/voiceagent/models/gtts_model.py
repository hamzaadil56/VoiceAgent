"""Custom TTS model provider for Google TTS (gTTS)."""

import io
import tempfile
from typing import AsyncIterator
from gtts import gTTS
import soundfile as sf
import numpy as np
from agents.voice import TTSModel, TTSModelSettings


class GTTSModel(TTSModel):
    """Text-to-speech model using Google TTS (gTTS)."""

    def __init__(self, language: str = "en"):
        """
        Initialize gTTS model.

        Args:
            language: Language code for TTS
        """
        self.language = language

    @property
    def model_name(self) -> str:
        """Return the model name."""
        return f"gtts-{self.language}"

    async def run(self, text: str, settings: TTSModelSettings) -> AsyncIterator[bytes]:
        """
        Synthesize text to speech using gTTS.

        The OpenAI Agents SDK expects PCM audio at 24kHz, 16-bit, mono.
        gTTS outputs MP3, so we need to convert it.

        Args:
            text: Text to synthesize
            settings: TTS model settings (voice, instructions, etc.)

        Yields:
            Audio chunks in PCM format (int16, 24kHz, mono)
        """
        # Generate speech using gTTS (outputs MP3)
        tts = gTTS(text=text, lang=self.language, slow=False)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
            tts.save(tmp_file.name)
            tmp_path = tmp_file.name

        try:
            # Read the MP3 file and convert to PCM
            audio_data, sample_rate = sf.read(tmp_path, dtype='float32')

            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)

            # Resample to 24kHz (OpenAI Agents SDK standard)
            if sample_rate != 24000:
                # Simple resampling (for production, use librosa or scipy for better quality)
                from scipy import signal
                num_samples = int(len(audio_data) * 24000 / sample_rate)
                audio_data = signal.resample(audio_data, num_samples)

            # Convert to int16 PCM format
            audio_int16 = (audio_data * 32767).astype(np.int16)

            # Convert to bytes
            audio_bytes = audio_int16.tobytes()

            # Yield in chunks (SDK expects streaming)
            chunk_size = 4096  # bytes
            for i in range(0, len(audio_bytes), chunk_size):
                chunk = audio_bytes[i:i + chunk_size]
                yield chunk

        finally:
            # Clean up temp file
            import os
            try:
                os.unlink(tmp_path)
            except:
                pass
