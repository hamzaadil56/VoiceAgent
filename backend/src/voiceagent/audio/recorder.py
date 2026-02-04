"""Audio recording with voice activity detection."""

import time
from typing import Optional
import sounddevice as sd
import numpy as np
from rich.console import Console

console = Console()


class AudioRecorder:
    """Records audio with automatic silence detection."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        silence_threshold: int = 500,
        silence_duration: float = 2.0,
    ):
        """
        Initialize audio recorder.

        Args:
            sample_rate: Sample rate in Hz
            channels: Number of audio channels
            chunk_size: Size of audio chunks to read
            silence_threshold: RMS threshold below which audio is considered silence
            silence_duration: Duration of silence (seconds) before stopping recording
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration

    def _calculate_rms(self, audio_chunk: np.ndarray) -> float:
        """Calculate RMS (Root Mean Square) of audio chunk."""
        return np.sqrt(np.mean(audio_chunk**2))

    def record(self, max_duration: Optional[float] = None) -> bytes:
        """
        Record audio until silence is detected or max duration reached.

        Args:
            max_duration: Maximum recording duration in seconds

        Returns:
            Recorded audio data as bytes
        """
        console.print("[bold green]🎤 Recording... Speak now![/bold green]")

        frames = []
        silent_chunks = 0
        chunks_for_silence = int(
            self.silence_duration * self.sample_rate / self.chunk_size)
        start_time = time.time()

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.int16,
                blocksize=self.chunk_size,
            ) as stream:
                while True:
                    # Check max duration
                    if max_duration and (time.time() - start_time) > max_duration:
                        console.print(
                            "[yellow]⏱️  Maximum duration reached[/yellow]")
                        break

                    # Read audio chunk
                    data, _ = stream.read(self.chunk_size)
                    frames.append(data.copy())

                    # Calculate volume and check for silence
                    rms = self._calculate_rms(data)

                    if rms < self.silence_threshold:
                        silent_chunks += 1
                        if silent_chunks >= chunks_for_silence:
                            console.print(
                                "[cyan]🔇 Silence detected, stopping recording[/cyan]")
                            break
                    else:
                        silent_chunks = 0

        except KeyboardInterrupt:
            console.print("[yellow]⏹️  Recording interrupted[/yellow]")

        # Concatenate all frames
        audio_array = np.concatenate(frames, axis=0)
        audio_data = audio_array.tobytes()

        duration = len(audio_data) / (self.sample_rate * self.channels * 2)
        console.print(f"[green]✓ Recording complete ({duration:.1f}s)[/green]")

        return audio_data

    def save_to_file(self, audio_data: bytes, filename: str) -> None:
        """Save audio data to WAV file."""
        import soundfile as sf

        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        # Reshape if stereo
        if self.channels > 1:
            audio_array = audio_array.reshape(-1, self.channels)

        # Convert to float for soundfile
        audio_float = audio_array.astype(np.float32) / 32768.0

        sf.write(filename, audio_float, self.sample_rate)
