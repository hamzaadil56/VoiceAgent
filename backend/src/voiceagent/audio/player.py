"""Audio playback functionality."""

import io
from typing import Union
import sounddevice as sd
import soundfile as sf
import numpy as np
from rich.console import Console

console = Console()


class AudioPlayer:
    """Plays audio from various sources."""

    def __init__(self):
        """Initialize audio player."""
        pass

    def play(self, audio_data: Union[bytes, str]) -> None:
        """
        Play audio from bytes or file path.

        Args:
            audio_data: Audio data as bytes or path to audio file
        """
        if isinstance(audio_data, str):
            self._play_from_file(audio_data)
        else:
            self._play_from_bytes(audio_data)

    def _play_from_bytes(self, audio_bytes: bytes) -> None:
        """Play audio from bytes."""
        console.print("[bold blue]🔊 Playing audio...[/bold blue]")

        try:
            # Read audio data from bytes
            audio_data, samplerate = sf.read(io.BytesIO(audio_bytes))

            # Play audio
            sd.play(audio_data, samplerate)
            sd.wait()  # Wait until playback is finished

        except Exception as e:
            console.print(f"[red]Error playing audio: {e}[/red]")
            # Try as raw PCM if soundfile fails
            try:
                # Assume 16-bit PCM, mono, 16kHz
                audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                audio_float = audio_array.astype(np.float32) / 32768.0
                sd.play(audio_float, 16000)
                sd.wait()
            except Exception as e2:
                console.print(f"[red]Failed to play audio: {e2}[/red]")
                return

        console.print("[green]✓ Playback complete[/green]")

    def _play_from_file(self, filepath: str) -> None:
        """Play audio from file."""
        console.print(
            f"[bold blue]🔊 Playing audio from {filepath}...[/bold blue]")

        try:
            # Read audio file
            audio_data, samplerate = sf.read(filepath)

            # Play audio
            sd.play(audio_data, samplerate)
            sd.wait()  # Wait until playback is finished

            console.print("[green]✓ Playback complete[/green]")

        except Exception as e:
            console.print(f"[red]Error playing file: {e}[/red]")
