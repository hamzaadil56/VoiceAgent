"""Agent System package for Voice Agent Platform."""

from .agent_builder import AgentBuilder, create_template_agent, get_available_templates

# Try to import TextAgent and VoiceAgentWrapper, but make them optional due to SSL certificate issues
try:
    from .text_agent import TextAgent
    _text_agent_available = True
except (PermissionError, OSError, ImportError) as e:
    # SSL certificate permission issues on macOS
    TextAgent = None
    _text_agent_available = False

try:
    from .voice_agent_wrapper import VoiceAgentWrapper
    _voice_agent_available = True
except (PermissionError, OSError, ImportError) as e:
    # SSL certificate permission issues or missing dependencies
    VoiceAgentWrapper = None
    _voice_agent_available = False

__all__ = [
    "AgentBuilder",
    "create_template_agent",
    "get_available_templates",
    "TextAgent",
    "VoiceAgentWrapper",
]
