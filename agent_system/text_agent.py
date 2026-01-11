"""Text Agent - Lightweight text-based agent for conversations."""

import asyncio
from typing import Optional, Dict, Any, List
from agents import Agent, Runner, ModelSettings

from voiceagent.models.groq_llm import create_groq_model
from voiceagent.config.settings import Settings


class TextAgent:
    """
    Text-based agent for chat conversations.
    
    Uses OpenAI Agents SDK with Groq LLM for text-only interactions.
    Optimized for Streamlit integration.
    """
    
    def __init__(
        self,
        name: str,
        instructions: str,
        groq_api_key: Optional[str] = None,
        llm_model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 500,
    ):
        """
        Initialize text agent.
        
        Args:
            name: Agent name
            instructions: System instructions/prompt
            groq_api_key: Groq API key (defaults to env var)
            llm_model: LLM model to use
            temperature: Generation temperature
            max_tokens: Maximum tokens
        """
        self.name = name
        self.instructions = instructions
        
        # Get API key from settings if not provided
        if not groq_api_key:
            settings = Settings()
            groq_api_key = settings.groq_api_key
        
        # Create Groq LLM model
        self.model = create_groq_model(
            api_key=groq_api_key,
            model=llm_model,
        )
        
        # Create agent
        self.agent = Agent(
            name=name,
            instructions=instructions,
            model=self.model,
            model_settings=ModelSettings(
                temperature=temperature,
                max_tokens=max_tokens,
            ),
        )
        
        # Message history for context
        self.message_history: List[Dict[str, str]] = []
    
    async def chat(self, user_message: str) -> str:
        """
        Send a message and get response.
        
        Args:
            user_message: User's message
            
        Returns:
            Agent's response text
        """
        try:
            # Run the agent with the user message
            result = await Runner.run(
                starting_agent=self.agent,
                input=user_message,
            )
            
            # Extract response text
            response_text = self._extract_response(result)
            
            # Store in history
            self.message_history.append({
                "role": "user",
                "content": user_message,
            })
            self.message_history.append({
                "role": "assistant",
                "content": response_text,
            })
            
            return response_text
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"TextAgent error: {error_msg}")
            return error_msg
    
    def _extract_response(self, result) -> str:
        """
        Extract text response from agent result.
        
        Args:
            result: Agent run result
            
        Returns:
            Response text
        """
        # Try different ways to extract the response
        if hasattr(result, "final_output") and result.final_output:
            return str(result.final_output)
        
        if hasattr(result, "messages") and result.messages:
            last_message = result.messages[-1]
            if hasattr(last_message, "content"):
                return str(last_message.content or "")
            elif isinstance(last_message, dict):
                return str(last_message.get("content", ""))
        
        if hasattr(result, "content") and result.content:
            return str(result.content)
        
        if hasattr(result, "text") and result.text:
            return str(result.text)
        
        # Fallback
        return str(result) if result else "I apologize, I couldn't generate a response."
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Get message history.
        
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        return self.message_history.copy()
    
    def clear_history(self):
        """Clear message history."""
        self.message_history = []
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "TextAgent":
        """
        Create TextAgent from configuration dictionary.
        
        Args:
            config: Agent configuration
            
        Returns:
            TextAgent instance
        """
        return cls(
            name=config.get("name", "Agent"),
            instructions=config.get("instructions", "You are a helpful assistant."),
            llm_model=config.get("llm_model", "llama-3.3-70b-versatile"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 500),
        )
    
    @classmethod
    def from_db_agent(cls, agent_data: Dict[str, Any]) -> "TextAgent":
        """
        Create TextAgent from database agent data.
        
        Args:
            agent_data: Agent data from database
            
        Returns:
            TextAgent instance
        """
        return cls.from_config(agent_data)


def run_text_agent_sync(agent: TextAgent, message: str) -> str:
    """
    Synchronous wrapper for running text agent (for Streamlit).
    
    Args:
        agent: TextAgent instance
        message: User message
        
    Returns:
        Agent response
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If there's already a running loop, create a new one
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(agent.chat(message))
        else:
            return asyncio.run(agent.chat(message))
    except Exception as e:
        print(f"Error in run_text_agent_sync: {str(e)}")
        return f"Error: {str(e)}"

