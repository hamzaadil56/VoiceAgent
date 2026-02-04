"""Voice Assistant Agent using OpenAI Agents SDK with Groq LLM."""

from typing import List, Dict, Any, Optional
from openai import OpenAI
from groq import Groq
from rich.console import Console

console = Console()


class VoiceAssistantAgent:
    """
    Voice Assistant Agent that uses Groq's LLM for conversation.

    This agent is designed for voice interactions, keeping responses
    concise and natural for spoken conversation.
    """

    def __init__(
        self,
        groq_api_key: str,
        model: str = "llama-3.3-70b-versatile",
        name: str = "VoiceAssistant",
        instructions: str = "You are a helpful voice assistant. Keep responses concise and natural.",
        max_tokens: int = 500,
        temperature: float = 0.7,
    ):
        """
        Initialize the Voice Assistant Agent.

        Args:
            groq_api_key: Groq API key
            model: LLM model to use
            name: Agent name
            instructions: System instructions for the agent
            max_tokens: Maximum tokens for response
            temperature: Temperature for sampling
        """
        self.client = Groq(api_key=groq_api_key)
        self.model = model
        self.name = name
        self.instructions = instructions
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []

        console.print(
            f"[bold green]✓ {self.name} initialized with {self.model}[/bold green]")

    def chat(self, user_message: str, reset_history: bool = False) -> str:
        """
        Process user message and generate response.

        Args:
            user_message: User's message
            reset_history: Whether to reset conversation history

        Returns:
            Agent's response
        """
        if reset_history:
            self.reset_conversation()

        console.print(f"[bold yellow]💭 User:[/bold yellow] {user_message}")

        # Add user message to history
        self.conversation_history.append(
            {"role": "user", "content": user_message})

        try:
            # Create messages with system instructions
            messages = [
                {"role": "system", "content": self.instructions}] + self.conversation_history

            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            assistant_message = response.choices[0].message.content

            # Add assistant response to history
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_message})

            console.print(
                f"[bold cyan]🤖 Agent:[/bold cyan] {assistant_message}")

            return assistant_message

        except Exception as e:
            console.print(f"[bold red]✗ Agent Error:[/bold red] {str(e)}")
            raise

    def reset_conversation(self) -> None:
        """Reset conversation history."""
        self.conversation_history = []
        console.print("[yellow]🔄 Conversation reset[/yellow]")

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()

    def set_instructions(self, instructions: str) -> None:
        """
        Update agent instructions.

        Args:
            instructions: New instructions
        """
        self.instructions = instructions
        console.print(f"[green]✓ Instructions updated[/green]")

    def add_context(self, context: str) -> None:
        """
        Add context to the conversation without user input.

        Args:
            context: Context to add
        """
        self.conversation_history.append(
            {"role": "system", "content": context})
        console.print(f"[blue]📝 Context added[/blue]")


class AgentWithTools(VoiceAssistantAgent):
    """
    Extended Voice Assistant Agent with tool/function calling capabilities.

    This demonstrates how to extend the base agent with tools.
    """

    def __init__(self, *args, tools: Optional[List[Dict[str, Any]]] = None, **kwargs):
        """
        Initialize agent with tools.

        Args:
            tools: List of tool definitions in OpenAI function format
        """
        super().__init__(*args, **kwargs)
        self.tools = tools or []

    def chat_with_tools(self, user_message: str) -> str:
        """
        Process user message with tool calling support.

        Args:
            user_message: User's message

        Returns:
            Agent's response
        """
        self.conversation_history.append(
            {"role": "user", "content": user_message})

        try:
            messages = [
                {"role": "system", "content": self.instructions}] + self.conversation_history

            # Call with tools if available
            if self.tools:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                )

            assistant_message = response.choices[0].message.content

            # Handle tool calls if present
            if hasattr(response.choices[0].message, "tool_calls") and response.choices[0].message.tool_calls:
                console.print(
                    "[magenta]🔧 Tool calls requested by agent[/magenta]")
                # Tool call handling would go here

            self.conversation_history.append(
                {"role": "assistant", "content": assistant_message})

            return assistant_message

        except Exception as e:
            console.print(f"[bold red]✗ Agent Error:[/bold red] {str(e)}")
            raise
