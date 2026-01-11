"""Text-to-Speech service using Orpheus TTS via LM Studio with SNAC decoder."""

import io
import wave
import json
from pathlib import Path
from typing import AsyncIterator
import httpx
from rich.console import Console
import re

from agents.voice import TTSModel, TTSModelSettings
from .orpheus_decoder import convert_to_audio, turn_token_into_id

console = Console()


class OrpheusTTSModel(TTSModel):
    """
    Text-to-Speech model using Orpheus TTS running on LM Studio with SNAC decoder.

    Based on: https://github.com/isaiahbjork/orpheus-tts-local

    IMPORTANT: Orpheus TTS requires the /completions endpoint (text completion),
    NOT /chat/completions (chat completion). This is why we use httpx directly.
    """

    # Available voices for Orpheus TTS
    VOICES = ["tara", "leah", "jess", "leo", "dan", "mia", "zac", "zoe"]

    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        voice: str = "tara",
        temperature: float = 0.6,
        top_p: float = 0.9,
        repetition_penalty: float = 1.1,
    ):
        """
        Initialize Orpheus TTS model.

        Args:
            base_url: LM Studio server URL
            voice: Voice to use (tara, leah, jess, leo, dan, mia, zac, zoe)
            temperature: Temperature for generation
            top_p: Top-p sampling parameter
            repetition_penalty: Repetition penalty
        """
        if voice not in self.VOICES:
            console.print(
                f"[yellow]⚠ Invalid voice '{voice}', using 'tara'[/yellow]")
            voice = "tara"

        # Use httpx to call /completions endpoint directly (NOT /chat/completions)
        self.base_url = base_url
        self.voice = voice
        self.temperature = temperature
        self.top_p = top_p
        self.repetition_penalty = repetition_penalty

        # Create output directory for generated audio files
        self.output_dir = Path("generated_audio")
        self.output_dir.mkdir(exist_ok=True)

        # Counter for unique filenames
        self.file_counter = 0

        console.print(
            f"[green]✓ Orpheus TTS ready (Voice: {voice}, Local LM Studio)[/green]"
        )

    @property
    def model_name(self) -> str:
        """The name of the TTS model."""
        return "orpheus-tts-local"

    def _format_prompt(self, text: str) -> str:
        """
        Format the text prompt for Orpheus TTS.
        Based on: https://github.com/isaiahbjork/orpheus-tts-local/blob/main/gguf_orpheus.py

        Args:
            text: The text to convert to speech

        Returns:
            Formatted prompt string
        """
        # Orpheus expects: <|audio|>{voice}: {text}<|eot_id|>
        return f"<|audio|>{self.voice}: {text}<|eot_id|>"

    async def run(
        self, text: str, settings: TTSModelSettings
    ) -> AsyncIterator[bytes]:
        """
        Given a text string, produces a stream of audio bytes, in PCM format.

        Args:
            text: The text to convert to audio.
            settings: TTS model settings

        Returns:
            An async iterator of audio bytes, in PCM format.
        """
        console.print(
            f"[bold magenta]🗣️  Synthesizing: {text[:50]}...[/bold magenta]")

        try:
            # Generate unique filename
            self.file_counter += 1
            output_file = self.output_dir / \
                f"orpheus_tts_{self.file_counter}.wav"

            # Format the prompt
            prompt = self._format_prompt(text)
            console.print(
                f"[cyan]Generating audio with Orpheus TTS ({self.voice})...[/cyan]")

            # Call LM Studio /completions endpoint with STREAMING
            # This is crucial - Orpheus TTS requires streaming to get custom tokens
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/completions",
                    json={
                        "model": "local-model",
                        "prompt": prompt,
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                        # Note: repeat_penalty, not repetition_penalty
                        "repeat_penalty": self.repetition_penalty,
                        "max_tokens": 1200,
                        "stream": True,  # MUST be True to get custom tokens
                    },
                    timeout=60.0,
                ) as response:
                    response.raise_for_status()

                    # Process streamed response
                    buffer = []
                    count = 0
                    audio_chunks = []
                    token_pattern = r'<custom_token_(\d+)>'

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str.strip() == "[DONE]":
                                break

                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    token_text = data["choices"][0].get(
                                        "text", "")

                                    # Extract custom tokens from streamed text
                                    token_matches = re.findall(
                                        token_pattern, token_text)

                                    for token_str in token_matches:
                                        # Reconstruct the token string
                                        token_id_str = f"<custom_token_{token_str}>"
                                        token = turn_token_into_id(
                                            token_id_str, count)

                                        if token is not None and token > 0:
                                            buffer.append(token)
                                            count += 1

                                            # Convert to audio when we have enough tokens
                                            if count % 7 == 0 and count > 27:
                                                buffer_to_proc = buffer[-28:]
                                                audio_samples = convert_to_audio(
                                                    buffer_to_proc, count
                                                )
                                                if audio_samples is not None:
                                                    audio_chunks.append(
                                                        audio_samples)

                            except json.JSONDecodeError:
                                continue

            if not audio_chunks:
                console.print(
                    f"[yellow]⚠ No audio generated (tokens extracted: {count})[/yellow]"
                )
                return

            console.print(
                f"[cyan]Extracted {count} tokens, generated {len(audio_chunks)} audio chunks[/cyan]"
            )

            # Combine all audio chunks
            full_audio = b"".join(audio_chunks)

            # Create WAV file
            audio_buffer = io.BytesIO()
            with wave.open(audio_buffer, "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(24000)  # 24kHz (SNAC standard)
                wav_file.writeframes(full_audio)

            wav_data = audio_buffer.getvalue()

            # Save to file
            with open(output_file, "wb") as f:
                f.write(wav_data)

            console.print(f"[green]✓ Audio saved to: {output_file}[/green]")
            console.print(
                f"[green]✓ Speech synthesized ({len(wav_data)} bytes)[/green]")

            # Yield in chunks
            chunk_size = 4096
            for i in range(0, len(wav_data), chunk_size):
                yield wav_data[i: i + chunk_size]

        except Exception as e:
            console.print(f"[bold red]✗ TTS Error:[/bold red] {str(e)}")
            import traceback
            console.print(f"[red]{traceback.format_exc()}[/red]")
            raise
