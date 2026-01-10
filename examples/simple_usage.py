#!/usr/bin/env python3
"""
Simple usage example of VoiceAgent.

This demonstrates the most basic usage pattern.
"""

from voiceagent import VoiceAgent
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def main():
    """Simple voice agent usage."""

    # Initialize voice agent with default settings
    agent = VoiceAgent()

    # Option 1: Run continuous conversation
    print("\n🎙️  Starting voice conversation...")
    print("Speak when prompted, and the agent will respond.\n")

    agent.run_conversation(max_turns=3)  # 3 turns demo

    # Option 2: Single voice interaction
    print("\n\n📝 Single interaction example:")
    user_text, agent_response, audio = agent.process_voice_input(
        play_response=True)
    print(f"You said: {user_text}")
    print(f"Agent replied: {agent_response}")

    # Option 3: Text-based interaction with voice response
    print("\n\n💬 Text chat with voice response:")
    response = agent.chat_text(
        "Hello, how are you today?", speak_response=True)
    print(f"Agent: {response}")


if __name__ == "__main__":
    main()
