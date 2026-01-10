#!/usr/bin/env python3
"""
Example: Programmatic usage of VoiceAgent components.

This shows how to use individual components separately
for custom integrations and workflows.
"""

from voiceagent.audio import AudioRecorder, AudioPlayer
from voiceagent.agent import VoiceAssistantAgent
from voiceagent.services import SpeechToTextService, TextToSpeechService
from voiceagent.config import Settings
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def example_stt_only():
    """Example: Use STT service standalone."""
    print("\n=== Speech-to-Text Only ===")

    settings = Settings()
    recorder = AudioRecorder(sample_rate=settings.sample_rate)
    stt = SpeechToTextService(api_key=settings.groq_api_key)

    # Record and transcribe
    audio_data = recorder.record(max_duration=5)
    text = stt.transcribe(audio_data, sample_rate=settings.sample_rate)

    print(f"Transcribed: {text}")


def example_tts_only():
    """Example: Use TTS service standalone."""
    print("\n=== Text-to-Speech Only ===")

    settings = Settings()
    tts = TextToSpeechService(api_key=settings.groq_api_key)
    player = AudioPlayer()

    # Synthesize and play
    text = "Hello! This is a text-to-speech demonstration."
    audio_bytes = tts.synthesize(text)
    player.play(audio_bytes)

    print("Audio played successfully")


def example_agent_only():
    """Example: Use Agent standalone (text chat)."""
    print("\n=== Agent Only (Text Chat) ===")

    settings = Settings()
    agent = VoiceAssistantAgent(
        groq_api_key=settings.groq_api_key,
        model=settings.llm_model,
    )

    # Chat interactions
    response1 = agent.chat("What's the weather like today?")
    print(f"Agent: {response1}")

    response2 = agent.chat("Tell me a fun fact about space.")
    print(f"Agent: {response2}")

    # View history
    history = agent.get_conversation_history()
    print(f"\nConversation had {len(history)} messages")


def example_custom_pipeline():
    """Example: Build custom pipeline with components."""
    print("\n=== Custom Pipeline ===")

    settings = Settings()

    # Initialize components
    recorder = AudioRecorder()
    stt = SpeechToTextService(api_key=settings.groq_api_key)
    agent = VoiceAssistantAgent(groq_api_key=settings.groq_api_key)
    tts = TextToSpeechService(api_key=settings.groq_api_key)
    player = AudioPlayer()

    # Custom workflow
    print("Recording...")
    audio = recorder.record(max_duration=5)

    print("Transcribing...")
    text = stt.transcribe(audio)
    print(f"User said: {text}")

    # Custom processing here (e.g., sentiment analysis, filtering, etc.)
    processed_text = f"[User sentiment: positive] {text}"

    print("Getting agent response...")
    response = agent.chat(processed_text)
    print(f"Agent response: {response}")

    print("Synthesizing speech...")
    audio_response = tts.synthesize(response)

    print("Playing response...")
    player.play(audio_response)

    print("Custom pipeline complete!")


def main():
    """Run examples."""
    print("\n╔═══════════════════════════════════════╗")
    print("║  Programmatic Usage Examples          ║")
    print("╚═══════════════════════════════════════╝")

    print("\nSelect example:")
    print("1. STT Only")
    print("2. TTS Only")
    print("3. Agent Only (Text Chat)")
    print("4. Custom Pipeline")

    choice = input("\nEnter choice (1-4): ").strip()

    if choice == "1":
        example_stt_only()
    elif choice == "2":
        example_tts_only()
    elif choice == "3":
        example_agent_only()
    elif choice == "4":
        example_custom_pipeline()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
