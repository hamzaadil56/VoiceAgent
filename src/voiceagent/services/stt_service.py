"""Speech-to-Text service using Groq Whisper."""

import io
import wave
from groq import Groq
from rich.console import Console

console = Console()


class SpeechToTextService:
    """Speech-to-Text service using Groq's Whisper models."""

    def __init__(self, api_key: str, model: str = "whisper-large-v3"):
        """
        Initialize STT service.

        Args:
            api_key: Groq API key
            model: Whisper model to use
        """
        self.client = Groq(api_key=api_key)
        self.model = model

    def transcribe(
        self,
        audio_data: bytes,
        sample_rate: int = 16000,
        channels: int = 1,
        language: str = "en",
    ) -> str:
        """
        Transcribe audio to text.

        Args:
            audio_data: Raw audio data as bytes
            sample_rate: Sample rate of audio
            channels: Number of audio channels
            language: Language code for transcription

        Returns:
            Transcribed text
        """
        console.print("[bold cyan]🎯 Transcribing audio...[/bold cyan]")

        try:
            # Convert raw audio to WAV format
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(sample_rate)
                wf.writeframes(audio_data)

            wav_buffer.seek(0)
            wav_buffer.name = "audio.wav"

            # Call Groq Whisper API
            transcription = self.client.audio.transcriptions.create(
                file=wav_buffer,
                model=self.model,
                language=language,
                response_format="text",
            )

            text = transcription.strip() if isinstance(transcription, str) else transcription.text

            console.print(f"[green]✓ Transcription:[/green] {text}")
            return text

        except Exception as e:
            console.print(f"[bold red]✗ STT Error:[/bold red] {str(e)}")
            raise

    def transcribe_file(self, filepath: str, language: str = "en") -> str:
        """
        Transcribe audio file to text.

        Args:
            filepath: Path to audio file
            language: Language code for transcription

        Returns:
            Transcribed text
        """
        console.print(f"[bold cyan]🎯 Transcribing file: {filepath}...[/bold cyan]")

        try:
            with open(filepath, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=(filepath, audio_file.read()),
                    model=self.model,
                    language=language,
                    response_format="text",
                )

            text = transcription.strip() if isinstance(transcription, str) else transcription.text

            console.print(f"[green]✓ Transcription:[/green] {text}")
            return text

        except Exception as e:
            console.print(f"[bold red]✗ STT Error:[/bold red] {str(e)}")
            raise

