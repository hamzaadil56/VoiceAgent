#!/usr/bin/env python3
"""
VoiceAgent - Main CLI Interface

A production-grade voice agent using OpenAI Agents SDK and Groq models.
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import box

from voiceagent import VoiceAgent, Settings


console = Console()


def print_banner():
    """Print welcome banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║           🎙️  VOICE AGENT                           ║
    ║                                                       ║
    ║     Powered by OpenAI Agents SDK & Groq Models       ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold blue")


def interactive_mode(agent: VoiceAgent):
    """Run in interactive mode with menu."""
    while True:
        console.print("\n[bold cyan]═══ Voice Agent Menu ═══[/bold cyan]\n")
        console.print("1. 🎙️  Start Voice Conversation")
        console.print("2. 💬 Text Chat (with voice response)")
        console.print("3. 📝 Text Chat (text only)")
        console.print("4. 🔄 Reset Conversation")
        console.print("5. 📊 View Conversation History")
        console.print("6. ⚙️  Update Instructions")
        console.print("7. 🚪 Exit")

        choice = console.input(
            "\n[bold yellow]Select option (1-7):[/bold yellow] ").strip()

        if choice == "1":
            console.print("\n")
            max_turns_input = console.input(
                "[cyan]Number of turns (press Enter for unlimited):[/cyan] "
            ).strip()
            max_turns = int(max_turns_input) if max_turns_input else None
            agent.run_conversation(max_turns=max_turns)

        elif choice == "2":
            text = console.input("\n[bold yellow]You:[/bold yellow] ")
            if text.strip():
                agent.chat_text(text, speak_response=True)

        elif choice == "3":
            text = console.input("\n[bold yellow]You:[/bold yellow] ")
            if text.strip():
                response = agent.chat_text(text, speak_response=False)
                console.print(f"[bold cyan]Agent:[/bold cyan] {response}")

        elif choice == "4":
            agent.reset()

        elif choice == "5":
            history = agent.get_conversation_history()
            if not history:
                console.print("\n[yellow]No conversation history[/yellow]")
            else:
                console.print(
                    "\n[bold cyan]═══ Conversation History ═══[/bold cyan]\n")
                for msg in history:
                    role = msg["role"].capitalize()
                    content = msg["content"]
                    color = "yellow" if msg["role"] == "user" else "cyan"
                    console.print(f"[{color}]{role}:[/{color}] {content}\n")

        elif choice == "6":
            instructions = console.input(
                "\n[cyan]Enter new instructions:[/cyan] "
            ).strip()
            if instructions:
                agent.update_agent_instructions(instructions)

        elif choice == "7":
            console.print("\n[bold green]👋 Goodbye![/bold green]\n")
            break

        else:
            console.print("\n[red]Invalid option. Please try again.[/red]")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="VoiceAgent - Production-grade voice agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--mode",
        choices=["voice", "text", "interactive"],
        default="interactive",
        help="Operation mode (default: interactive)",
    )

    parser.add_argument(
        "--turns",
        type=int,
        default=None,
        help="Maximum conversation turns (for voice mode)",
    )

    parser.add_argument(
        "--message",
        type=str,
        help="Text message to send (for text mode)",
    )

    parser.add_argument(
        "--no-voice-response",
        action="store_true",
        help="Disable voice response in text mode",
    )

    parser.add_argument(
        "--instructions",
        type=str,
        help="Custom agent instructions",
    )

    args = parser.parse_args()

    try:
        # Print banner
        print_banner()

        # Initialize VoiceAgent
        console.print("\n[dim]Loading configuration...[/dim]")
        settings = Settings()

        # Apply custom instructions if provided
        if args.instructions:
            settings.agent_instructions = args.instructions

        agent = VoiceAgent(settings)

        # Run based on mode
        if args.mode == "interactive":
            interactive_mode(agent)

        elif args.mode == "voice":
            console.print(
                "\n[bold cyan]Starting voice conversation...[/bold cyan]\n")
            agent.run_conversation(max_turns=args.turns)

        elif args.mode == "text":
            if not args.message:
                console.print(
                    "[red]Error: --message required for text mode[/red]")
                sys.exit(1)

            response = agent.chat_text(
                args.message,
                speak_response=not args.no_voice_response,
            )

            if args.no_voice_response:
                console.print(f"\n[bold cyan]Agent:[/bold cyan] {response}")

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        import traceback

        console.print(f"\n[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    main()
