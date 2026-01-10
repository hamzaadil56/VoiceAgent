"""Text-to-Speech service using Google TTS (gTTS) - free, no API key needed."""

from gtts import gTTS
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

        # Create output directory for generated audio files
        self.output_dir = Path("generated_audio")
        self.output_dir.mkdir(exist_ok=True)

        # Counter for unique filenames
        self.file_counter = 0

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
            # Generate unique filename
            self.file_counter += 1
            output_file = self.output_dir / \
                f"tts_output_{self.file_counter}.mp3"

            # Generate speech using gTTS
            console.print(f"[cyan]Generating audio with Google TTS...[/cyan]")

            tts = gTTS(text=text, lang=self.language, slow=self.slow)
            tts.save(str(output_file))

            # Read the generated file
            with open(output_file, 'rb') as f:
                audio_data = f.read()

            console.print(f"[green]✓ Audio saved to: {output_file}[/green]")
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
