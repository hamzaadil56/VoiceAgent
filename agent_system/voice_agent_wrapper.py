"""Voice Agent Wrapper - Integration with existing VoiceAgent."""

import asyncio
import numpy as np
from typing import Optional, Dict, Any
from pathlib import Path

from voiceagent import VoiceAgent, Settings


class VoiceAgentWrapper:
    """
    Wrapper around the existing VoiceAgent for Streamlit integration.
    
    Provides simplified interface for voice conversations with data collection.
    """
    
    def __init__(
        self,
        name: str,
        instructions: str,
        groq_api_key: Optional[str] = None,
        llm_model: str = "llama-3.3-70b-versatile",
        stt_model: str = "whisper-large-v3",
        tts_voice: str = "tara",
        temperature: float = 0.7,
        max_tokens: int = 500,
        lm_studio_url: str = "http://localhost:1234/v1",
    ):
        """
        Initialize voice agent wrapper.
        
        Args:
            name: Agent name
            instructions: System instructions/prompt
            groq_api_key: Groq API key
            llm_model: LLM model
            stt_model: Speech-to-text model
            tts_voice: Text-to-speech voice
            temperature: Generation temperature
            max_tokens: Maximum tokens
            lm_studio_url: LM Studio URL for TTS
        """
        self.name = name
        self.instructions = instructions
        
        # Create settings
        settings = Settings()
        
        # Override with custom values
        settings.agent_name = name
        settings.agent_instructions = instructions
        settings.llm_model = llm_model
        settings.stt_model = stt_model
        settings.tts_voice = tts_voice
        settings.temperature = temperature
        settings.max_tokens = max_tokens
        settings.lm_studio_url = lm_studio_url
        
        if groq_api_key:
            settings.groq_api_key = groq_api_key
        
        # Initialize the voice agent
        self.agent = VoiceAgent(settings)
        
        # Store last transcription and response
        self.last_transcription: Optional[str] = None
        self.last_response_text: Optional[str] = None
        self.last_audio_response: Optional[bytes] = None
    
    async def process_audio(
        self,
        audio_data: np.ndarray,
        play_response: bool = True,
    ) -> tuple[str, str, bytes]:
        """
        Process audio input through the voice pipeline.
        
        Args:
            audio_data: Audio data as numpy array
            play_response: Whether to play the audio response
            
        Returns:
            Tuple of (transcription, response_text, audio_bytes)
        """
        # Process through the voice agent
        transcription, audio_response = await self.agent.process_voice_input(
            audio_data,
            play_response=play_response,
        )
        
        # Store for later access
        self.last_transcription = transcription
        self.last_audio_response = audio_response
        
        # For voice pipeline, we need to extract the text response
        # This is a limitation - the voice pipeline doesn't directly return text response
        # We'll use the transcription as a proxy for now
        # In a production system, you'd want to modify VoiceAgent to return both
        self.last_response_text = "(Voice response - audio only)"
        
        return transcription, self.last_response_text, audio_response
    
    async def process_text(self, user_message: str) -> str:
        """
        Process text message and get voice response.
        
        Args:
            user_message: User's text message
            
        Returns:
            Agent's text response
        """
        response = await self.agent.chat_text(user_message, speak_response=False)
        self.last_response_text = response
        return response
    
    async def process_text_with_voice(self, user_message: str) -> tuple[str, bytes]:
        """
        Process text message and generate voice response.
        
        Args:
            user_message: User's text message
            
        Returns:
            Tuple of (response_text, audio_bytes)
        """
        # Process text to get response
        response_text = await self.process_text(user_message)
        
        # Generate audio for the response
        # This would require access to the TTS model
        # For now, we'll just return empty audio
        audio_bytes = b""
        
        return response_text, audio_bytes
    
    def record_audio(self, duration: int = 5) -> np.ndarray:
        """
        Record audio from microphone.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Audio data as numpy array
        """
        return self.agent.record_audio(duration=duration)
    
    def save_audio(self, audio_data: bytes, filename: str) -> Path:
        """
        Save audio data to file.
        
        Args:
            audio_data: Audio bytes
            filename: Output filename
            
        Returns:
            Path to saved file
        """
        output_path = self.agent.output_dir / filename
        with open(output_path, "wb") as f:
            f.write(audio_data)
        return output_path
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "VoiceAgentWrapper":
        """
        Create VoiceAgentWrapper from configuration dictionary.
        
        Args:
            config: Agent configuration
            
        Returns:
            VoiceAgentWrapper instance
        """
        return cls(
            name=config.get("name", "Voice Agent"),
            instructions=config.get("instructions", "You are a helpful voice assistant."),
            llm_model=config.get("llm_model", "llama-3.3-70b-versatile"),
            stt_model=config.get("stt_model", "whisper-large-v3"),
            tts_voice=config.get("tts_voice", "tara"),
            temperature=config.get("temperature", 0.7),
            max_tokens=config.get("max_tokens", 500),
        )
    
    @classmethod
    def from_db_agent(cls, agent_data: Dict[str, Any]) -> "VoiceAgentWrapper":
        """
        Create VoiceAgentWrapper from database agent data.
        
        Args:
            agent_data: Agent data from database
            
        Returns:
            VoiceAgentWrapper instance
        """
        return cls.from_config(agent_data)


def run_voice_agent_sync(
    agent: VoiceAgentWrapper,
    audio_data: np.ndarray,
    play_response: bool = True,
) -> tuple[str, str, bytes]:
    """
    Synchronous wrapper for voice agent (for Streamlit).
    
    Args:
        agent: VoiceAgentWrapper instance
        audio_data: Audio numpy array
        play_response: Whether to play response
        
    Returns:
        Tuple of (transcription, response_text, audio_bytes)
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(
                agent.process_audio(audio_data, play_response)
            )
        else:
            return asyncio.run(agent.process_audio(audio_data, play_response))
    except Exception as e:
        print(f"Error in run_voice_agent_sync: {str(e)}")
        return "", f"Error: {str(e)}", b""

