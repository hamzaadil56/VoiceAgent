"""Voice service wrapper for WebSocket integration."""

import io
import os
import subprocess
import tempfile
import wave
import base64
from typing import AsyncIterator, Optional

import numpy as np
from voiceagent import VoiceAgent, Settings

from backend.logging_config import get_logger

logger = get_logger(__name__)


class VoiceService:
    """Service layer for voice agent operations via WebSocket."""

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize voice service.

        Args:
            settings: VoiceAgent settings
        """
        self.settings = settings or Settings()
        self.agent: Optional[VoiceAgent] = None
        self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the VoiceAgent instance."""
        try:
            self.agent = VoiceAgent(self.settings)
            logger.info("VoiceService initialized")
        except Exception as e:
            logger.exception("Failed to initialize VoiceAgent: %s", e)
            raise

    def update_settings(self, **kwargs):
        """Update agent settings and reinitialize."""
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                # Validate max_turns if provided
                if key == "max_turns" and value is not None:
                    value = max(1, min(5, int(value)))  # Clamp between 1 and 5
                setattr(self.settings, key, value)
        self._initialize_agent()

    def _convert_webm_to_wav(self, webm_data: bytes) -> bytes:
        """
        Convert WebM audio to WAV format using ffmpeg (if available).

        Args:
            webm_data: WebM audio data as bytes

        Returns:
            WAV audio data as bytes
        """
        try:
            # Check if ffmpeg is available
            subprocess.run(['ffmpeg', '-version'],
                           capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("ffmpeg not found. WebM conversion may fail.")
            raise RuntimeError("ffmpeg not available for WebM conversion")

        try:
            # Create temporary files
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as webm_file:
                webm_file.write(webm_data)
                webm_path = webm_file.name

            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
                wav_path = wav_file.name

            # Convert using ffmpeg
            result = subprocess.run(
                [
                    'ffmpeg', '-i', webm_path,
                    '-ar', '24000',  # Sample rate
                    '-ac', '1',      # Mono
                    '-f', 'wav',
                    '-y',            # Overwrite output
                    wav_path
                ],
                check=True,
                capture_output=True
            )

            # Read WAV file
            with open(wav_path, 'rb') as f:
                wav_data = f.read()

            # Cleanup
            os.unlink(webm_path)
            os.unlink(wav_path)

            return wav_data
        except Exception as e:
            logger.warning("Could not convert WebM to WAV: %s", e)
            raise

    async def process_audio_chunk(
        self, audio_data: bytes, sample_rate: int = 24000
    ) -> tuple[str, AsyncIterator[bytes]]:
        """
        Process audio chunk through the voice agent.

        Args:
            audio_data: Audio data as bytes (WebM or WAV format)
            sample_rate: Sample rate of the audio

        Returns:
            Tuple of (transcribed_text, audio_response_iterator)
        """
        if not self.agent:
            raise RuntimeError("VoiceAgent not initialized")

        # Convert bytes to numpy array
        audio_array = None
        try:
            # Try to read as WAV first
            audio_io = io.BytesIO(audio_data)
            with wave.open(audio_io, "rb") as wav_file:
                sample_rate = wav_file.getframerate()
                n_channels = wav_file.getnchannels()
                audio_bytes = wav_file.readframes(wav_file.getnframes())
                audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        except Exception as e1:
            logger.debug("Not WAV format, trying WebM conversion: %s", e1)
            # If not WAV, try to convert WebM to WAV
            try:
                wav_data = self._convert_webm_to_wav(audio_data)
                audio_io = io.BytesIO(wav_data)
                with wave.open(audio_io, "rb") as wav_file:
                    sample_rate = wav_file.getframerate()
                    audio_bytes = wav_file.readframes(wav_file.getnframes())
                    audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            except Exception as e2:
                logger.warning("Could not process audio format: %s. Trying raw PCM.", e2)
                # Last resort: assume raw PCM at 24kHz
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                sample_rate = 24000

        # Ensure mono and correct format
        if len(audio_array.shape) > 1:
            audio_array = audio_array[:, 0]
        audio_array = audio_array.flatten()

        # Resample if needed (VoiceAgent expects 24kHz)
        if sample_rate != 24000:
            from scipy import signal
            num_samples = int(len(audio_array) * 24000 / sample_rate)
            audio_array = signal.resample(
                audio_array, num_samples).astype(np.int16)

        # Process through voice agent
        transcribed_text, audio_response = await self.agent.process_voice_input(
            audio_array, play_response=False
        )

        # Extract PCM data from audio response
        # Create async iterator for streaming PCM audio chunks
        async def pcm_audio_iterator():
            try:
                pcm_data = None

                if isinstance(audio_response, np.ndarray):
                    # Convert numpy array directly to PCM bytes
                    pcm_data = audio_response.tobytes()
                    logger.debug("Converted numpy array to PCM: %s bytes", len(pcm_data))
                elif isinstance(audio_response, bytes):
                    # If it's WAV bytes, extract PCM from WAV
                    pcm_data = self._extract_pcm_from_wav(audio_response)
                    if not pcm_data:
                        logger.error("Failed to extract PCM from WAV")
                        return
                    logger.debug("Extracted PCM from WAV: %s bytes", len(pcm_data))
                else:
                    logger.error("Unexpected audio_response type: %s", type(audio_response))
                    return

                if not pcm_data:
                    logger.error("No PCM data available")
                    return

                logger.debug("PCM data ready: %s bytes", len(pcm_data))

                # Stream PCM in smaller chunks for real-time playback
                chunk_size = 4096  # Stream in 4KB chunks
                chunk_count = 0

                for i in range(0, len(pcm_data), chunk_size):
                    pcm_chunk = pcm_data[i: i + chunk_size]
                    chunk_count += 1
                    yield pcm_chunk

                logger.debug("Streamed %s PCM chunks", chunk_count)

            except Exception as e:
                logger.exception("PCM streaming error: %s", e)
                raise

        return transcribed_text, pcm_audio_iterator()

    async def process_text_message(self, text: str) -> tuple[str, AsyncIterator[bytes]]:
        """
        Process text message and get voice response as PCM stream.

        Args:
            text: User's text message

        Returns:
            Tuple of (response_text, pcm_audio_iterator)
        """
        if not self.agent:
            raise RuntimeError("VoiceAgent not initialized")

        # Get text response
        response_text = await self.agent.chat_text(text, speak_response=False)

        # Generate audio response
        logger.debug("Generating audio for: %s", response_text[:80] + "..." if len(response_text) > 80 else response_text)

        # Synthesize speech using the TTS model from voice pipeline
        from agents.voice import TTSModelSettings

        # Stream PCM audio chunks as they're generated
        async def pcm_audio_iterator():
            try:
                # Collect all WAV chunks first (TTS streams one complete WAV in chunks)
                logger.debug("Collecting TTS chunks...")
                wav_chunks = []
                async for wav_chunk in self.agent._tts_model.run(response_text, TTSModelSettings()):
                    wav_chunks.append(wav_chunk)

                # Combine into complete WAV file
                complete_wav = b''.join(wav_chunks)
                logger.debug("Complete WAV collected: %s bytes", len(complete_wav))

                # Extract PCM from complete WAV file
                pcm_data = self._extract_pcm_from_wav(complete_wav)

                if not pcm_data:
                    logger.error("Failed to extract PCM from WAV")
                    return

                logger.debug("Extracted PCM: %s bytes", len(pcm_data))

                # Stream PCM in smaller chunks for real-time playback
                chunk_size = 4096  # Stream in 4KB chunks
                chunk_count = 0

                for i in range(0, len(pcm_data), chunk_size):
                    pcm_chunk = pcm_data[i:i + chunk_size]
                    chunk_count += 1
                    yield pcm_chunk

                logger.debug("Streamed %s PCM chunks", chunk_count)

            except Exception as e:
                logger.exception("TTS Error: %s", e)
                raise

        return response_text, pcm_audio_iterator()

    def _extract_pcm_from_wav(self, wav_data: bytes) -> Optional[bytes]:
        """
        Extract raw PCM data from WAV file(s).
        Handles single WAV file or multiple concatenated WAV files.

        Args:
            wav_data: WAV file bytes (may contain multiple WAV files concatenated)

        Returns:
            Raw PCM data (Int16) or None if extraction fails
        """
        try:
            all_pcm_chunks = []
            position = 0
            wav_count = 0

            # Handle multiple WAV files that may be concatenated
            # Each WAV file starts with "RIFF" header at position 0
            while position < len(wav_data):
                # Check if we have a valid WAV header at current position
                if position + 12 > len(wav_data):
                    break

                # Check for "RIFF" header
                if wav_data[position:position + 4] != b'RIFF':
                    # Try to find next "RIFF" header
                    next_riff = wav_data.find(b'RIFF', position + 1)
                    if next_riff == -1:
                        # No more WAV files found
                        break
                    position = next_riff

                # Read file size from WAV header (offset 4, size 4 bytes, little-endian)
                file_size = int.from_bytes(
                    wav_data[position + 4:position + 8], byteorder='little')
                wav_file_end = position + 8 + file_size

                # Make sure we have enough data
                if wav_file_end > len(wav_data):
                    # Try to read as much as we have
                    wav_file_end = len(wav_data)

                # Extract this WAV file
                wav_file_data = wav_data[position:wav_file_end]

                try:
                    wav_io = io.BytesIO(wav_file_data)
                    with wave.open(wav_io, 'rb') as wav_file:
                        if wav_count == 0:
                            logger.debug(
                                "WAV info: %s ch, %s Hz, %s bytes/sample, %s frames",
                                wav_file.getnchannels(),
                                wav_file.getframerate(),
                                wav_file.getsampwidth(),
                                wav_file.getnframes(),
                            )
                        # Read the PCM data (skip the WAV header)
                        pcm_chunk = wav_file.readframes(wav_file.getnframes())
                        if pcm_chunk:
                            all_pcm_chunks.append(pcm_chunk)
                            wav_count += 1
                            logger.debug("Extracted PCM from WAV %s: %s bytes", wav_count, len(pcm_chunk))
                except Exception as e:
                    logger.warning(
                        "Could not extract WAV %s at position %s: %s",
                        wav_count + 1,
                        position,
                        e,
                    )
                    # Move position forward to try next potential WAV file
                    # Try to find next RIFF header
                    next_riff = wav_data.find(b'RIFF', position + 1)
                    if next_riff == -1:
                        break
                    position = next_riff
                    continue

                # Move to next potential WAV file
                position = wav_file_end

            if wav_count == 0:
                # Fallback: try reading as single WAV file
                try:
                    wav_io = io.BytesIO(wav_data)
                    with wave.open(wav_io, 'rb') as wav_file:
                        logger.debug(
                            "WAV info: %s ch, %s Hz, %s bytes/sample, %s frames",
                            wav_file.getnchannels(),
                            wav_file.getframerate(),
                            wav_file.getsampwidth(),
                            wav_file.getnframes(),
                        )
                        pcm_data = wav_file.readframes(wav_file.getnframes())
                        if pcm_data:
                            logger.debug("Extracted PCM from single WAV: %s bytes", len(pcm_data))
                            return pcm_data
                except Exception as e:
                    logger.warning("Could not read as single WAV: %s", e)

                logger.error("Could not extract PCM from any WAV file")
                return None

            # Combine all PCM chunks
            combined_pcm = b"".join(all_pcm_chunks)
            logger.debug(
                "Extracted PCM from %s WAV file(s): %s total bytes",
                wav_count,
                len(combined_pcm),
            )
            return combined_pcm

        except Exception as e:
            logger.exception("Error extracting PCM from WAV: %s", e)
            return None

    def get_available_voices(self) -> list[str]:
        """Get list of available TTS voices."""
        return ["tara", "leah", "jess", "leo", "dan", "mia", "zac", "zoe"]

    def get_settings(self) -> dict:
        """Get current settings as dictionary."""
        return {
            "agent_name": self.settings.agent_name,
            "tts_voice": self.settings.tts_voice,
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_tokens,
            "stt_model": self.settings.stt_model,
            "llm_model": self.settings.llm_model,
            "max_turns": self.settings.max_turns,
        }
