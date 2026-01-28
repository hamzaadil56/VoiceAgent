#!/usr/bin/env python3
"""
VoiceAgent - Main CLI Interface

A production-grade voice agent using OpenAI Agents SDK with Groq models.
"""

import sys
import asyncio
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
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
    ║        Powered by OpenAI Agents SDK & Groq           ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold blue")


def show_menu():
    """Display the main menu."""
    table = Table(
        title="🎙️ Voice Agent - Main Menu",
        box=box.ROUNDED,
        show_header=False,
        title_style="bold cyan",
    )
    table.add_column("Option", style="bold yellow", width=10)
    table.add_column("Description", style="white")

    table.add_row("1", "🎤 Start Voice Conversation")
    table.add_row("2", "💬 Text Chat with Voice Response")
    table.add_row("3", "📝 Text-Only Chat (No Voice)")
    table.add_row("4", "⚙️  Configure Agent Settings")
    table.add_row("5", "🎯 Quick Test")
    table.add_row("6", "ℹ️  System Information")
    table.add_row("0", "🚪 Exit")

    console.print()
    console.print(table)
    console.print()


async def voice_conversation_mode(agent: VoiceAgent):
    """Run voice conversation mode."""
    console.print(
        Panel(
            "[bold green]Voice Conversation Mode[/bold green]\n\n"
            "Speak naturally when prompted. The agent will listen and respond.\n"
            "Press Ctrl+C to return to menu.",
            title="🎤 Voice Mode",
            expand=False,
        )
    )

    turns = Prompt.ask(
        "\n[cyan]How many conversation turns?[/cyan]",
        default="unlimited"
    )

    max_turns = None if turns.lower() == "unlimited" else int(turns)

    try:
        await agent.run_conversation(max_turns=max_turns)
    except KeyboardInterrupt:
        console.print("\n[yellow]Returning to menu...[/yellow]")


async def text_with_voice_mode(agent: VoiceAgent):
    """Run text input with voice response mode."""
    console.print(
        Panel(
            "[bold green]Text Chat with Voice Response[/bold green]\n\n"
            "Type your messages and get voice responses.\n"
            "Type 'back', 'exit', or 'quit' to return to menu.",
            title="💬 Text + Voice Mode",
            expand=False,
        )
    )

    while True:
        console.print()
        user_input = Prompt.ask("[bold cyan]You[/bold cyan]")

        if user_input.lower() in ["back", "exit", "quit"]:
            console.print("[yellow]Returning to menu...[/yellow]")
            break

        if not user_input.strip():
            continue

        try:
            # Process text and get voice response
            await agent.chat_text(user_input, speak_response=True)
            console.print()  # Add spacing between exchanges
        except KeyboardInterrupt:
            console.print(
                "\n[yellow]Interrupted. Returning to menu...[/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            if not Confirm.ask("[yellow]Continue?[/yellow]", default=True):
                break


async def text_only_mode(agent: VoiceAgent):
    """Run text-only chat mode (no voice)."""
    console.print(
        Panel(
            "[bold green]Text-Only Chat Mode[/bold green]\n\n"
            "Pure text conversation without voice synthesis.\n"
            "Type 'back', 'exit', or 'quit' to return to menu.",
            title="📝 Text-Only Mode",
            expand=False,
        )
    )

    while True:
        console.print()
        user_input = Prompt.ask("[bold cyan]You[/bold cyan]")

        if user_input.lower() in ["back", "exit", "quit"]:
            console.print("[yellow]Returning to menu...[/yellow]")
            break

        if not user_input.strip():
            continue

        try:
            # Process text without voice
            await agent.chat_text(user_input, speak_response=False)
            console.print()  # Add spacing between exchanges
        except KeyboardInterrupt:
            console.print(
                "\n[yellow]Interrupted. Returning to menu...[/yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            if not Confirm.ask("[yellow]Continue?[/yellow]", default=True):
                break


def configure_settings(settings: Settings):
    """Configure agent settings interactively."""
    console.print(
        Panel(
            "[bold green]Configure Agent Settings[/bold green]",
            title="⚙️ Settings",
            expand=False,
        )
    )

    console.print("\n[dim]Press Enter to keep current value[/dim]\n")

    # Agent name
    new_name = Prompt.ask(
        "[cyan]Agent Name[/cyan]",
        default=settings.agent_name
    )
    settings.agent_name = new_name

    # Agent instructions
    console.print(
        f"\n[cyan]Current Instructions:[/cyan] {settings.agent_instructions[:100]}...")
    if Confirm.ask("\n[cyan]Update agent instructions?[/cyan]", default=False):
        new_instructions = Prompt.ask("[cyan]New Instructions[/cyan]")
        settings.agent_instructions = new_instructions

    # Temperature
    new_temp = Prompt.ask(
        "[cyan]Temperature (0.0-1.0)[/cyan]",
        default=str(settings.temperature)
    )
    settings.temperature = float(new_temp)

    # Max tokens
    new_tokens = Prompt.ask(
        "[cyan]Max Tokens[/cyan]",
        default=str(settings.max_tokens)
    )
    settings.max_tokens = int(new_tokens)

    # TTS Voice
    available_voices = ["tara", "leah", "jess",
                        "leo", "dan", "mia", "zac", "zoe"]
    console.print(
        f"\n[cyan]Available Voices:[/cyan] {', '.join(available_voices)}")
    new_voice = Prompt.ask(
        "[cyan]TTS Voice[/cyan]",
        default=settings.tts_voice,
        choices=available_voices
    )
    settings.tts_voice = new_voice

    console.print("\n[bold green]✓ Settings updated![/bold green]")
    console.print(
        "[yellow]Note: Restart the agent to apply all changes.[/yellow]")


async def quick_test(agent: VoiceAgent):
    """Run a quick test of the voice agent."""
    console.print(
        Panel(
            "[bold green]Quick Test Mode[/bold green]\n\n"
            "This will record 5 seconds of audio and process it.\n"
            "Get ready to speak!",
            title="🎯 Quick Test",
            expand=False,
        )
    )

    if not Confirm.ask("\n[cyan]Start test?[/cyan]", default=True):
        return

    try:
        # Record a single turn
        await agent.run_conversation(max_turns=1)
        console.print(
            "\n[bold green]✓ Test completed successfully![/bold green]")
    except Exception as e:
        console.print(f"\n[bold red]✗ Test failed:[/bold red] {str(e)}")


def show_system_info(settings: Settings):
    """Display system and configuration information."""
    table = Table(
        title="ℹ️ System Information",
        box=box.ROUNDED,
        show_header=True,
        title_style="bold cyan",
    )
    table.add_column("Component", style="bold yellow")
    table.add_column("Value", style="white")

    # Models
    table.add_row("STT Model", f"{settings.stt_model} (Groq)")
    table.add_row("LLM Model", f"{settings.llm_model} (Groq)")
    table.add_row("TTS Model", f"Orpheus TTS (LM Studio)")
    table.add_row("TTS Voice", settings.tts_voice)

    # Configuration
    table.add_row("", "")  # Separator
    table.add_row("Agent Name", settings.agent_name)
    table.add_row("Temperature", str(settings.temperature))
    table.add_row("Max Tokens", str(settings.max_tokens))

    # Audio settings
    table.add_row("", "")  # Separator
    table.add_row("Sample Rate", f"{settings.sample_rate} Hz")
    table.add_row("Channels", str(settings.channels))
    table.add_row("Silence Threshold", str(settings.silence_threshold))

    # API Configuration
    table.add_row("", "")  # Separator
    table.add_row("LM Studio URL", settings.lm_studio_url)
    table.add_row("Groq API Key", "***" +
                  settings.groq_api_key[-4:] if len(settings.groq_api_key) > 4 else "***")

    console.print()
    console.print(table)
    console.print()


async def interactive_menu():
    """Run the interactive menu."""
    print_banner()

    # Initialize settings and agent
    console.print("\n[dim]Loading configuration...[/dim]")
    settings = Settings()

    console.print("[dim]Initializing voice agent...[/dim]\n")
    agent = VoiceAgent(settings)

    console.print(
        Panel(
            "[bold green]✓ Voice Agent Ready![/bold green]\n\n"
            "All systems initialized and ready to go.",
            title="Status",
            expand=False,
        )
    )

    # Main menu loop
    while True:
        show_menu()

        choice = Prompt.ask(
            "[bold yellow]Select an option[/bold yellow]",
            choices=["0", "1", "2", "3", "4", "5", "6"],
            default="1"
        )

        try:
            if choice == "1":
                await voice_conversation_mode(agent)
            elif choice == "2":
                await text_with_voice_mode(agent)
            elif choice == "3":
                await text_only_mode(agent)
            elif choice == "4":
                configure_settings(settings)
                # Reinitialize agent with new settings
                console.print(
                    "\n[dim]Reinitializing agent with new settings...[/dim]")
                agent = VoiceAgent(settings)
            elif choice == "5":
                await quick_test(agent)
            elif choice == "6":
                show_system_info(settings)
            elif choice == "0":
                console.print(
                    "\n[bold cyan]👋 Thank you for using Voice Agent![/bold cyan]\n")
                break

        except KeyboardInterrupt:
            console.print("\n[yellow]Returning to menu...[/yellow]")
            continue
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")

            if not Confirm.ask("\n[yellow]Continue?[/yellow]", default=True):
                break


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="VoiceAgent - Production-grade voice agent with OpenAI Agents SDK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["interactive", "voice", "text"],
        default="interactive",
        help="Execution mode: interactive (menu), voice (direct conversation), or text (text chat)",
    )

    parser.add_argument(
        "--turns",
        type=int,
        default=None,
        help="Maximum conversation turns (default: unlimited)",
    )

    parser.add_argument(
        "--instructions",
        type=str,
        help="Custom agent instructions",
    )

    parser.add_argument(
        "--message",
        type=str,
        help="Single message for text mode",
    )

    parser.add_argument(
        "--no-voice-response",
        action="store_true",
        help="Disable voice response in text mode",
    )

    args = parser.parse_args()

    try:
        if args.mode == "interactive":
            # Run interactive menu
            await interactive_menu()
        else:
            # Run direct modes
            print_banner()
            console.print("\n[dim]Loading configuration...[/dim]")
            settings = Settings()

            # Apply custom instructions if provided
            if args.instructions:
                settings.agent_instructions = args.instructions

            # Create the voice agent
            agent = VoiceAgent(settings)

            if args.mode == "voice":
                # Voice conversation mode
                console.print(
                    "\n[bold cyan]Starting voice conversation...[/bold cyan]\n")
                await agent.run_conversation(max_turns=args.turns)
            elif args.mode == "text":
                # Text mode
                if args.message:
                    console.print(f"\n[cyan]User:[/cyan] {args.message}")
                    console.print(
                        "[yellow]Note: Text mode requires extending VoiceAgent class.[/yellow]")
                else:
                    console.print(
                        "[bold red]Error:[/bold red] --message required for text mode")
                    sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        import traceback
        console.print(f"\n[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
