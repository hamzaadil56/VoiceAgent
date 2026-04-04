"""
VoiceAgent - Voice pipeline using OpenAI Agents SDK.

Uses the SDK's VoicePipeline with Groq-backed models:
- STT: Groq Whisper
- LLM: Groq Llama (via LiteLLM)
- TTS: Groq PlayAI TTS
"""

from ..models.groq_llm import create_groq_model
from ..models import GroqVoiceModelProvider
from ..config.settings import Settings
from agents.extensions.handoff_prompt import prompt_with_handoff_instructions
from agents.voice import (
    VoicePipeline,
    SingleAgentVoiceWorkflow,
    AudioInput,
    VoicePipelineConfig,
)
from agents import Agent, set_tracing_disabled, Runner
import warnings
import numpy as np
from typing import Optional
from rich.console import Console

try:
    import sounddevice as sd
except (OSError, ImportError):
    # Optional local playback (install `local-audio` extra) or no PortAudio
    sd = None

# Suppress Pydantic warnings from LiteLLM
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


console = Console()


class VoiceAgent:
    """
    Voice Agent using OpenAI Agents SDK VoicePipeline.

    Architecture:
    Audio Input → Groq STT → Agent (Groq LLM) → Groq PlayAI TTS → Audio Output
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize VoiceAgent with OpenAI Agents SDK.

        Args:
            settings: Configuration settings
        """
        self.settings = settings or Settings()

        # Disable tracing if no OpenAI key (since we're using Groq)
        set_tracing_disabled(True)

        console.print(
            "[bold blue]🚀 Initializing VoiceAgent with OpenAI Agents SDK...[/bold blue]")

        # Create Groq LLM model using LiteLLM
        groq_model = create_groq_model(
            api_key=self.settings.groq_api_key,
            model=self.settings.llm_model,
        )

        # Create the agent using OpenAI Agents SDK
        # Model settings (temperature, max_tokens) are passed via the Agent
        from agents import ModelSettings

        self.agent = Agent(
            name=self.settings.agent_name,
            instructions=prompt_with_handoff_instructions(
                self.settings.agent_instructions
            ),
            model=groq_model,
            model_settings=ModelSettings(
                temperature=self.settings.temperature,
                max_tokens=self.settings.max_tokens,
            ),
        )

        voice_provider = GroqVoiceModelProvider(
            groq_api_key=self.settings.groq_api_key,
            stt_model=self.settings.stt_model,
            tts_model=self.settings.tts_model,
            tts_voice=self.settings.tts_voice,
        )

        # Create voice pipeline config
        config = VoicePipelineConfig(
            model_provider=voice_provider,
        )

        # Create the voice pipeline with our agent
        workflow = SingleAgentVoiceWorkflow(self.agent)
        self.pipeline = VoicePipeline(workflow=workflow, config=config)

        # Store TTS model instance for text chat
        self._tts_model = voice_provider.get_tts_model(None)

        console.print(
            "[bold green]✓ VoiceAgent ready with OpenAI Agents SDK![/bold green]")
        console.print(f"[cyan]  STT: {self.settings.stt_model} (Groq)[/cyan]")
        console.print(f"[cyan]  LLM: {self.settings.llm_model} (Groq)[/cyan]")
        console.print(
            f"[cyan]  TTS: {self.settings.tts_model} / {self.settings.tts_voice} (Groq)[/cyan]")

    async def process_voice_input(
        self, audio_buffer: np.ndarray, play_response: bool = True
    ) -> tuple[str, bytes]:
        """
        Process voice input through the pipeline.

        Args:
            audio_buffer: Audio data as numpy array
            play_response: Whether to play the audio response

        Returns:
            Tuple of (transcribed_text, audio_response_bytes)
        """
        console.print("[bold green]🎤 Processing voice input...[/bold green]")

        # Create AudioInput from buffer
        audio_input = AudioInput(buffer=audio_buffer)

        # Run the voice pipeline
        result = await self.pipeline.run(audio_input)

        # Collect audio chunks
        audio_chunks = []
        transcribed_text = ""

        # Stream and optionally play the response
        player = None
        if play_response and sd is not None:
            player = sd.OutputStream(
                samplerate=24000, channels=1, dtype=np.int16
            )
            player.start()

        try:
            async for event in result.stream():
                if event.type == "voice_stream_event_audio":
                    audio_chunks.append(event.data)
                    if play_response and player:
                        player.write(event.data)
                elif event.type == "voice_stream_event_transcript":
                    transcribed_text = event.text
        finally:
            if player:
                player.stop()
                player.close()

        # Combine all audio chunks (SDK emits numpy int16 arrays)
        audio_response = b"".join(
            c.tobytes() if isinstance(c, np.ndarray) else bytes(c) for c in audio_chunks
        )

        console.print(f"[green]✓ Transcription:[/green] {transcribed_text}")
        console.print(
            f"[green]✓ Generated {len(audio_response)} bytes of audio[/green]")

        return transcribed_text, audio_response

    def record_audio(self, duration: int = 5) -> np.ndarray:
        """
        Record audio from microphone.

        Args:
            duration: Recording duration in seconds

        Returns:
            Audio data as numpy array
        """
        if sd is None:
            raise RuntimeError(
                "PortAudio/sounddevice not available (e.g. serverless). "
                "Recording requires a local audio device."
            )
        console.print(
            f"[bold green]🎤 Recording for {duration} seconds...[/bold green]")

        # Record audio
        sample_rate = 24000  # OpenAI Agents SDK uses 24kHz
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.int16,
        )
        sd.wait()

        console.print("[green]✓ Recording complete[/green]")
        return recording.flatten()

    async def run_conversation(self, max_turns: Optional[int] = None):
        """
        Run a continuous voice conversation.

        Args:
            max_turns: Maximum number of conversation turns
        """
        console.print(
            "\n[bold blue]╔═══════════════════════════════════════╗[/bold blue]")
        console.print(
            "[bold blue]║   🎙️  VOICE AGENT CONVERSATION      ║[/bold blue]")
        console.print(
            "[bold blue]╚═══════════════════════════════════════╝[/bold blue]\n")
        console.print("[dim]Press Ctrl+C to exit[/dim]\n")

        turn = 0
        try:
            while max_turns is None or turn < max_turns:
                turn += 1
                console.print(
                    f"\n[bold white]═══ Turn {turn} ═══[/bold white]\n")

                # Record audio
                audio_buffer = self.record_audio(duration=5)

                # Process through pipeline
                await self.process_voice_input(audio_buffer, play_response=True)

                console.print("")

        except KeyboardInterrupt:
            console.print(
                "\n\n[bold yellow]👋 Conversation ended by user[/bold yellow]")
        except Exception as e:
            console.print(f"\n\n[bold red]❌ Error: {str(e)}[/bold red]")
            import traceback
            console.print(f"[red]{traceback.format_exc()}[/red]")
        finally:
            console.print(f"\n[dim]Total turns: {turn}[/dim]\n")

    async def chat_text(self, user_message: str, speak_response: bool = True) -> str:
        """
        Process a text message and get agent response using OpenAI Agents SDK.

        Args:
            user_message: User's text message
            speak_response: Whether to synthesize and play voice response

        Returns:
            Agent's text response
        """
        console.print(f"[bold cyan]💬 You:[/bold cyan] {user_message}")

        try:
            # Use Runner.run() to process text through the agent
            # This is the correct way to run an agent in OpenAI Agents SDK
            result = await Runner.run(
                starting_agent=self.agent,
                input=user_message
            )

            # Extract text response from agent result
            # RunResult has a final_output attribute
            response_text = ""

            # Try to extract the final output text
            if hasattr(result, "final_output"):
                response_text = result.final_output or ""
            elif hasattr(result, "messages") and result.messages:
                # Get the last message which should be the assistant's response
                last_message = result.messages[-1]
                if hasattr(last_message, "content"):
                    response_text = last_message.content or ""
                elif isinstance(last_message, dict):
                    response_text = last_message.get("content", "")
            elif hasattr(result, "content") and result.content:
                response_text = result.content
            elif isinstance(result, str):
                response_text = result
            elif hasattr(result, "text"):
                response_text = result.text
            else:
                # Fallback: convert to string
                response_text = str(result)

            if not response_text or response_text.strip() == "":
                response_text = "I apologize, but I couldn't generate a response. Please try again."

            console.print(f"[bold green]🤖 Agent:[/bold green] {response_text}")

            # Synthesize and play voice if requested
            if speak_response and response_text:
                await self._synthesize_and_play(response_text)

            return response_text

        except Exception as e:
            console.print(f"[bold red]✗ Error:[/bold red] {str(e)}")
            import traceback
            console.print(f"[red]{traceback.format_exc()}[/red]")
            raise

    async def _synthesize_and_play(self, text: str):
        """
        Synthesize text to speech and play it.

        Args:
            text: Text to synthesize
        """
        from agents.voice import TTSModelSettings
        import io

        try:
            console.print("[dim]🎵 Generating speech...[/dim]")

            # Use TTS model to generate audio
            audio_chunks = []
            async for chunk in self._tts_model.run(text, TTSModelSettings()):
                audio_chunks.append(chunk)

            if not audio_chunks:
                console.print("[yellow]⚠ No audio generated[/yellow]")
                return

            # Combine chunks (GroqTTSModel yields raw int16 PCM at 24 kHz)
            audio_data = b"".join(audio_chunks)

            # Play audio using sounddevice (when available)
            if sd is not None:
                try:
                    if len(audio_data) >= 4 and audio_data[:4] == b"RIFF":
                        import soundfile as sf

                        audio_io = io.BytesIO(audio_data)
                        audio_array, sample_rate = sf.read(audio_io, dtype="float32")
                        if len(audio_array.shape) > 1:
                            audio_array = audio_array[:, 0]
                        max_val = abs(audio_array).max() if len(audio_array) > 0 else 1.0
                        if max_val > 0:
                            audio_array = audio_array / max_val
                        console.print("[dim]🔊 Playing response...[/dim]")
                        sd.play(audio_array, samplerate=sample_rate)
                        sd.wait()
                    else:
                        pcm = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                        if len(pcm) == 0:
                            console.print("[yellow]⚠ No audio samples[/yellow]")
                            return
                        console.print("[dim]🔊 Playing response...[/dim]")
                        sd.play(pcm, samplerate=24000)
                        sd.wait()
                except ImportError:
                    console.print("[dim]🔊 Playback skipped (install soundfile for WAV fallback)[/dim]")
                except Exception as e:
                    console.print(
                        f"[yellow]⚠ Could not play audio: {str(e)}[/yellow]")
            else:
                console.print("[dim]🔊 Playback skipped (no audio device)[/dim]")

        except Exception as e:
            console.print(f"[yellow]⚠ TTS Error: {str(e)}[/yellow]")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")
