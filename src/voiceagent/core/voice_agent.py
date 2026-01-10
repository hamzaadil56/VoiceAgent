"""
VoiceAgent - Main orchestrator for voice-based AI interactions.

This module ties together STT, Agent, and TTS into a seamless pipeline.
"""

from typing import Optional
from rich.console import Console

from ..config.settings import Settings
from ..audio.recorder import AudioRecorder
from ..audio.player import AudioPlayer
from ..services.stt_service import SpeechToTextService
from ..services.tts_service import TextToSpeechService
from ..agent.voice_assistant_agent import VoiceAssistantAgent

console = Console()


class VoiceAgent:
    """
    Main VoiceAgent orchestrator that manages the complete voice interaction pipeline:
    Audio Input → STT → Agent → TTS → Audio Output
    """

    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize VoiceAgent with all required components.

        Args:
            settings: Configuration settings (loads from .env if not provided)
        """
        # Load settings
        self.settings = settings or Settings()

        # Initialize components
        console.print("[bold blue]🚀 Initializing VoiceAgent...[/bold blue]")

        # Audio components
        self.recorder = AudioRecorder(
            sample_rate=self.settings.sample_rate,
            channels=self.settings.channels,
            chunk_size=self.settings.chunk_size,
            silence_threshold=self.settings.silence_threshold,
            silence_duration=self.settings.silence_duration,
        )
        self.player = AudioPlayer()

        # STT service
        self.stt = SpeechToTextService(
            api_key=self.settings.groq_api_key,
            model=self.settings.stt_model,
        )

        # TTS service
        self.tts = TextToSpeechService(
            api_key=self.settings.groq_api_key,
            model=self.settings.tts_model,
        )

        # Agent
        self.agent = VoiceAssistantAgent(
            groq_api_key=self.settings.groq_api_key,
            model=self.settings.llm_model,
            name=self.settings.agent_name,
            instructions=self.settings.agent_instructions,
            max_tokens=self.settings.max_tokens,
            temperature=self.settings.temperature,
        )

        console.print("[bold green]✓ VoiceAgent ready![/bold green]")

    def process_voice_input(self, play_response: bool = True) -> tuple[str, str, Optional[bytes]]:
        """
        Process a single voice interaction:
        1. Record audio
        2. Transcribe to text
        3. Get agent response
        4. Synthesize to speech
        5. Play audio (optional)

        Args:
            play_response: Whether to play the audio response

        Returns:
            Tuple of (transcribed_text, agent_response, audio_bytes)
        """
        # Step 1: Record audio
        audio_data = self.recorder.record(max_duration=self.settings.record_seconds)

        # Step 2: Transcribe
        transcribed_text = self.stt.transcribe(
            audio_data,
            sample_rate=self.settings.sample_rate,
            channels=self.settings.channels,
        )

        if not transcribed_text or transcribed_text.strip() == "":
            console.print("[yellow]⚠️  No speech detected[/yellow]")
            return "", "", None

        # Step 3: Get agent response
        agent_response = self.agent.chat(transcribed_text)

        # Step 4: Synthesize speech
        audio_bytes = self.tts.synthesize(agent_response)

        # Step 5: Play audio (optional)
        if play_response and audio_bytes:
            self.player.play(audio_bytes)

        return transcribed_text, agent_response, audio_bytes

    def chat_text(self, text: str, speak_response: bool = True) -> str:
        """
        Text-based chat (bypass STT).

        Args:
            text: User's text input
            speak_response: Whether to synthesize and play the response

        Returns:
            Agent's response
        """
        console.print(f"[bold yellow]💭 User (text):[/bold yellow] {text}")

        # Get agent response
        agent_response = self.agent.chat(text)

        # Optionally synthesize and play
        if speak_response:
            audio_bytes = self.tts.synthesize(agent_response)
            self.player.play(audio_bytes)

        return agent_response

    def run_conversation(self, max_turns: Optional[int] = None) -> None:
        """
        Run a continuous voice conversation.

        Args:
            max_turns: Maximum number of conversation turns (None for unlimited)
        """
        console.print("\n[bold blue]╔═══════════════════════════════════════╗[/bold blue]")
        console.print("[bold blue]║   🎙️  VOICE AGENT CONVERSATION      ║[/bold blue]")
        console.print("[bold blue]╚═══════════════════════════════════════╝[/bold blue]\n")
        console.print("[dim]Press Ctrl+C to exit[/dim]\n")

        turn = 0
        try:
            while max_turns is None or turn < max_turns:
                turn += 1
                console.print(f"\n[bold white]═══ Turn {turn} ═══[/bold white]\n")

                # Process voice input
                self.process_voice_input(play_response=True)

                console.print("")

        except KeyboardInterrupt:
            console.print("\n\n[bold yellow]👋 Conversation ended by user[/bold yellow]")
        except Exception as e:
            console.print(f"\n\n[bold red]❌ Error: {str(e)}[/bold red]")
            raise
        finally:
            console.print(f"\n[dim]Total turns: {turn}[/dim]\n")

    def reset(self) -> None:
        """Reset the agent's conversation history."""
        self.agent.reset_conversation()
        console.print("[green]✓ VoiceAgent reset[/green]")

    def update_agent_instructions(self, instructions: str) -> None:
        """
        Update the agent's instructions.

        Args:
            instructions: New instructions for the agent
        """
        self.agent.set_instructions(instructions)

    def get_conversation_history(self) -> list:
        """Get the conversation history."""
        return self.agent.get_conversation_history()

