#!/usr/bin/env python3
"""
Example: Custom Voice Agent with specific personality and domain expertise.

This example shows how to create a domain-specific voice agent
(e.g., fitness coach, language tutor, technical support).
"""

from voiceagent import VoiceAgent, Settings
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def create_fitness_coach():
    """Create a fitness coach voice agent."""
    settings = Settings()
    settings.agent_name = "FitnessCoach"
    settings.agent_instructions = """
    You are an enthusiastic and supportive fitness coach named Coach Alex.
    
    Your role:
    - Motivate users to achieve their fitness goals
    - Provide workout suggestions and form tips
    - Give nutritional advice for healthy living
    - Track progress and celebrate achievements
    - Keep responses concise and energetic (2-3 sentences max)
    - Use encouraging language and fitness terminology
    
    Remember: Safety first! Always remind users to consult healthcare providers
    before starting new fitness routines.
    """

    return VoiceAgent(settings)


def create_language_tutor():
    """Create a language tutor voice agent."""
    settings = Settings()
    settings.agent_name = "LanguageTutor"
    settings.agent_instructions = """
    You are a patient and encouraging language tutor specializing in conversational practice.
    
    Your role:
    - Help users practice speaking in their target language
    - Correct pronunciation and grammar gently
    - Provide contextual vocabulary
    - Use simple, clear speech suitable for learners
    - Keep responses at an appropriate difficulty level
    - Encourage continued practice
    
    Start by asking what language they want to practice.
    """

    return VoiceAgent(settings)


def create_tech_support():
    """Create a technical support voice agent."""
    settings = Settings()
    settings.agent_name = "TechSupport"
    settings.agent_instructions = """
    You are a friendly and knowledgeable technical support specialist.
    
    Your role:
    - Help users troubleshoot technical issues
    - Explain technical concepts in simple terms
    - Provide step-by-step instructions
    - Ask clarifying questions to understand the problem
    - Be patient and avoid technical jargon
    - Keep instructions clear and concise
    
    Always confirm understanding before moving to the next step.
    """

    return VoiceAgent(settings)


def main():
    """Run example with menu selection."""
    from rich.console import Console

    console = Console()

    console.print(
        "\n[bold cyan]═══ Custom Voice Agent Examples ═══[/bold cyan]\n")
    console.print("1. 💪 Fitness Coach")
    console.print("2. 🗣️  Language Tutor")
    console.print("3. 🔧 Tech Support")
    console.print("4. 🚪 Exit")

    choice = console.input(
        "\n[bold yellow]Select agent (1-4):[/bold yellow] ").strip()

    if choice == "1":
        console.print("\n[bold green]Starting Fitness Coach...[/bold green]")
        agent = create_fitness_coach()
    elif choice == "2":
        console.print("\n[bold green]Starting Language Tutor...[/bold green]")
        agent = create_language_tutor()
    elif choice == "3":
        console.print("\n[bold green]Starting Tech Support...[/bold green]")
        agent = create_tech_support()
    elif choice == "4":
        console.print("\n[bold green]Goodbye![/bold green]")
        return
    else:
        console.print("\n[red]Invalid choice[/red]")
        return

    # Run conversation
    agent.run_conversation()


if __name__ == "__main__":
    main()
