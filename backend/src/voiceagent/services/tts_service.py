"""Text-to-Speech service using Google TTS (gTTS) - free, no API key needed."""

from gtts import gTTS
import tempfile
from pathlib import Path
from rich.console import Console

console = Console()


class TextToSpeechService:
    """Text-to-Speech service using Google TTS (free, no API key required)."""

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize TTS service for Google TTS.

        Args:
            api_key: Not used (kept for compatibility with Groq services)
            model: Not used (kept for compatibility)
        """
        self.language = "en"
        self.slow = False

        console.print(
            f"[green]✓ Google TTS ready (free, no API key needed)[/green]")

    def synthesize(self, text: str, voice: str = None) -> bytes:
        """
        Synthesize text to speech using Google TTS.

        Args:
            text: Text to synthesize
            voice: Not used (gTTS uses Google's default voice)

        Returns:
            Audio data as bytes in MP3 format
        """
        console.print(
            f"[bold magenta]🗣️  Synthesizing: {text[:50]}...[/bold magenta]")

        try:
            # Generate speech using gTTS
            console.print(f"[cyan]Generating audio with Google TTS...[/cyan]")

            # Use temporary file to avoid saving to disk permanently
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tmp_path = tmp_file.name
                tts = gTTS(text=text, lang=self.language, slow=self.slow)
                tts.save(tmp_path)

            # Read the generated file
            try:
                with open(tmp_path, 'rb') as f:
                    audio_data = f.read()
            finally:
                # Clean up temporary file
                import os
                try:
                    os.unlink(tmp_path)
                except:
                    pass

            console.print(
                f"[green]✓ Speech synthesized ({len(audio_data)} bytes)[/green]")
            return audio_data

        except Exception as e:
            console.print(f"[bold red]✗ TTS Error:[/bold red] {str(e)}")
            import traceback
            console.print(f"[red]{traceback.format_exc()}[/red]")
            raise

    def synthesize_to_file(self, text: str, filepath: str, voice: str = None) -> None:
        """
        Synthesize text to speech and save to file.

        Args:
            text: Text to synthesize
            filepath: Output file path
            voice: Not used (gTTS uses Google's default voice)
        """
        try:
            console.print(f"[cyan]Generating audio for: {text}[/cyan]")

            tts = gTTS(text=text, lang=self.language, slow=self.slow)
            tts.save(filepath)

            console.print(f"[green]✓ Audio saved to {filepath}[/green]")

        except Exception as e:
            console.print(f"[bold red]✗ TTS Error:[/bold red] {str(e)}")
            import traceback
            console.print(f"[red]{traceback.format_exc()}[/red]")
            raise
