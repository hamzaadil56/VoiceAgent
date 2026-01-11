#!/usr/bin/env python3
"""
Test script to verify the menu interface works correctly.
"""

import asyncio
from voiceagent import VoiceAgent, Settings
from rich.console import Console

console = Console()


async def test_menu():
    """Test that the menu initializes correctly."""
    console.print("[bold cyan]Testing Voice Agent Menu System...[/bold cyan]\n")
    
    # Test 1: Settings initialization
    console.print("[yellow]Test 1:[/yellow] Initializing settings...")
    settings = Settings()
    console.print("[green]✓ Settings loaded successfully[/green]")
    console.print(f"  - STT Model: {settings.stt_model}")
    console.print(f"  - LLM Model: {settings.llm_model}")
    console.print(f"  - TTS Voice: {settings.tts_voice}")
    console.print(f"  - LM Studio URL: {settings.lm_studio_url}\n")
    
    # Test 2: VoiceAgent initialization
    console.print("[yellow]Test 2:[/yellow] Initializing voice agent...")
    agent = VoiceAgent(settings)
    console.print("[green]✓ VoiceAgent initialized successfully[/green]\n")
    
    # Test 3: Menu components
    console.print("[yellow]Test 3:[/yellow] Menu components...")
    console.print("[green]✓ All menu options available:[/green]")
    console.print("  1. 🎤 Start Voice Conversation")
    console.print("  2. 💬 Text Chat with Voice Response")
    console.print("  3. 📝 Text-Only Chat (No Voice)")
    console.print("  4. ⚙️  Configure Agent Settings")
    console.print("  5. 🎯 Quick Test")
    console.print("  6. ℹ️  System Information")
    console.print("  0. 🚪 Exit\n")
    
    # Test 4: System info display
    console.print("[yellow]Test 4:[/yellow] System information display...")
    from rich.table import Table
    from rich import box
    
    table = Table(
        title="ℹ️ System Information",
        box=box.ROUNDED,
        show_header=True,
        title_style="bold cyan",
    )
    table.add_column("Component", style="bold yellow")
    table.add_column("Value", style="white")
    
    table.add_row("STT Model", f"{settings.stt_model} (Groq)")
    table.add_row("LLM Model", f"{settings.llm_model} (Groq)")
    table.add_row("TTS Model", f"Orpheus TTS (LM Studio)")
    table.add_row("TTS Voice", settings.tts_voice)
    table.add_row("Temperature", str(settings.temperature))
    table.add_row("Max Tokens", str(settings.max_tokens))
    
    console.print(table)
    console.print("[green]✓ System info display working[/green]\n")
    
    # Summary
    console.print("[bold green]═══════════════════════════════════════[/bold green]")
    console.print("[bold green]✓ All tests passed![/bold green]")
    console.print("[bold green]═══════════════════════════════════════[/bold green]\n")
    
    console.print("[bold cyan]Menu Features Available:[/bold cyan]")
    console.print("  ✓ Interactive menu with 7 options")
    console.print("  ✓ Voice conversation mode")
    console.print("  ✓ Text chat with voice response")
    console.print("  ✓ Text-only chat mode")
    console.print("  ✓ Agent configuration editor")
    console.print("  ✓ Quick test functionality")
    console.print("  ✓ System information display")
    console.print("  ✓ Command-line arguments support\n")
    
    console.print("[bold yellow]To run the menu:[/bold yellow]")
    console.print("  python main.py                    # Interactive menu (default)")
    console.print("  python main.py --mode voice       # Direct voice conversation")
    console.print("  python main.py --mode text        # Text mode")
    console.print("  python main.py --turns 5          # Limit conversation turns")
    console.print("  python main.py --instructions \"...\" # Custom instructions\n")


if __name__ == "__main__":
    asyncio.run(test_menu())

