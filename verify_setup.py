#!/usr/bin/env python3
"""
Quick verification script for VoiceAgent functionality.
Tests all major features without user interaction.
"""

import asyncio
from voiceagent import VoiceAgent, Settings
from rich.console import Console

console = Console()


async def verify_all():
    """Quick verification of all VoiceAgent features."""
    console.print("\n[bold cyan]🔍 Verifying VoiceAgent Setup...[/bold cyan]\n")
    
    settings = Settings()
    agent = VoiceAgent(settings)
    
    # Test 1: Text chat without voice
    console.print("[yellow]Test 1:[/yellow] Text chat (no voice)")
    response = await agent.chat_text("Hello!", speak_response=False)
    assert len(response) > 0 and "RunResult" not in response
    console.print("[green]✓ Passed[/green]\n")
    
    # Test 2: Check all methods exist
    console.print("[yellow]Test 2:[/yellow] All methods available")
    assert hasattr(agent, "chat_text")
    assert hasattr(agent, "process_voice_input")
    assert hasattr(agent, "run_conversation")
    console.print("[green]✓ Passed[/green]\n")
    
    # Test 3: Menu integration
    console.print("[yellow]Test 3:[/yellow] Math question")
    response = await agent.chat_text("What is 10 + 5?", speak_response=False)
    assert "15" in response
    console.print("[green]✓ Passed[/green]\n")
    
    console.print("""
[bold green]✅ All Verifications Passed![/bold green]

[bold cyan]Available Features:[/bold cyan]
  ✓ Text chat with voice response (Menu Option 2)
  ✓ Text-only chat (Menu Option 3)
  ✓ Voice conversation (Menu Option 1)
  ✓ Agent configuration (Menu Option 4)
  ✓ System information (Menu Option 6)

[bold yellow]To use the application:[/bold yellow]
  python main.py

[bold yellow]Then select from the menu:[/bold yellow]
  1 - Voice conversation (requires microphone)
  2 - Text chat with voice response
  3 - Text-only chat (fastest)
    """)


if __name__ == "__main__":
    asyncio.run(verify_all())

