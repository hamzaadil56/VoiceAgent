"""Agent Builder - Create and configure voice agents."""

from typing import Dict, Any, Optional
from enum import Enum


class AgentTemplate(Enum):
    """Pre-defined agent templates."""
    
    STARTUP_VALIDATOR = "startup_validator"
    INTERVIEWER = "interviewer"
    CUSTOMER_SERVICE = "customer_service"
    FEEDBACK_COLLECTOR = "feedback_collector"
    SURVEY = "survey"


class AgentBuilder:
    """Builder class for creating and configuring agents."""
    
    # Available voices for Orpheus TTS
    AVAILABLE_VOICES = ["tara", "leah", "jess", "leo", "dan", "mia", "zac", "zoe"]
    
    # Available categories
    CATEGORIES = [
        "Interview",
        "Customer Service",
        "Survey",
        "Feedback",
        "Validation",
        "Education",
        "Healthcare",
        "Sales",
        "Support",
        "Other",
    ]
    
    def __init__(self):
        """Initialize agent builder with defaults."""
        self.config = {
            "name": "",
            "description": "",
            "instructions": "",
            "llm_model": "llama-3.3-70b-versatile",
            "stt_model": "whisper-large-v3",
            "tts_voice": "tara",
            "temperature": 0.7,
            "max_tokens": 500,
            "category": "Other",
            "is_active": True,
        }
    
    def set_name(self, name: str) -> "AgentBuilder":
        """Set agent name."""
        self.config["name"] = name
        return self
    
    def set_description(self, description: str) -> "AgentBuilder":
        """Set agent description."""
        self.config["description"] = description
        return self
    
    def set_instructions(self, instructions: str) -> "AgentBuilder":
        """Set agent instructions/system prompt."""
        self.config["instructions"] = instructions
        return self
    
    def set_llm_model(self, model: str) -> "AgentBuilder":
        """Set LLM model."""
        self.config["llm_model"] = model
        return self
    
    def set_voice(self, voice: str) -> "AgentBuilder":
        """Set TTS voice."""
        if voice not in self.AVAILABLE_VOICES:
            raise ValueError(f"Voice must be one of {self.AVAILABLE_VOICES}")
        self.config["tts_voice"] = voice
        return self
    
    def set_temperature(self, temperature: float) -> "AgentBuilder":
        """Set generation temperature."""
        if not 0.0 <= temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        self.config["temperature"] = temperature
        return self
    
    def set_max_tokens(self, max_tokens: int) -> "AgentBuilder":
        """Set maximum tokens."""
        if max_tokens < 1:
            raise ValueError("Max tokens must be positive")
        self.config["max_tokens"] = max_tokens
        return self
    
    def set_category(self, category: str) -> "AgentBuilder":
        """Set agent category."""
        self.config["category"] = category
        return self
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate agent configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.config["name"]:
            return False, "Agent name is required"
        
        if not self.config["instructions"]:
            return False, "Agent instructions are required"
        
        if len(self.config["name"]) > 255:
            return False, "Agent name must be less than 255 characters"
        
        if self.config["tts_voice"] not in self.AVAILABLE_VOICES:
            return False, f"Invalid voice. Must be one of {self.AVAILABLE_VOICES}"
        
        return True, None
    
    def build(self) -> Dict[str, Any]:
        """
        Build and return agent configuration.
        
        Returns:
            Agent configuration dictionary
        
        Raises:
            ValueError: If configuration is invalid
        """
        is_valid, error = self.validate()
        if not is_valid:
            raise ValueError(f"Invalid agent configuration: {error}")
        
        return self.config.copy()
    
    @classmethod
    def from_template(cls, template: AgentTemplate) -> "AgentBuilder":
        """
        Create an agent builder from a template.
        
        Args:
            template: Agent template to use
            
        Returns:
            AgentBuilder instance configured with template
        """
        builder = cls()
        
        if template == AgentTemplate.STARTUP_VALIDATOR:
            builder.set_name("Startup Idea Validator")
            builder.set_description(
                "Validate your startup idea through structured questions. "
                "Get expert feedback on your problem, solution, market, and go-to-market strategy."
            )
            builder.set_instructions(
                "You are an expert startup advisor helping entrepreneurs validate their ideas. "
                "Ask the following questions one by one:\n\n"
                "1. What problem does your startup solve?\n"
                "2. Who are your target customers?\n"
                "3. What makes your solution unique compared to alternatives?\n"
                "4. How will you make money? What's your revenue model?\n"
                "5. What is your go-to-market strategy?\n\n"
                "After each answer:\n"
                "- Acknowledge their response\n"
                "- Provide brief, constructive feedback (1-2 sentences)\n"
                "- Ask the next question\n\n"
                "Be encouraging but honest. At the end, provide a summary of strengths and areas to improve."
            )
            builder.set_category("Validation")
            builder.set_temperature(0.7)
        
        elif template == AgentTemplate.INTERVIEWER:
            builder.set_name("Job Interview Agent")
            builder.set_description(
                "Practice your job interview skills with an AI interviewer. "
                "Answer common interview questions and get feedback."
            )
            builder.set_instructions(
                "You are a professional job interviewer conducting a screening interview. "
                "Ask the following questions one by one:\n\n"
                "1. Tell me about yourself and your background.\n"
                "2. What are your key strengths?\n"
                "3. Describe a challenging situation you faced and how you handled it.\n"
                "4. Where do you see yourself in 5 years?\n"
                "5. Do you have any questions for me?\n\n"
                "Be professional, friendly, and encouraging. "
                "After each answer, acknowledge and ask the next question. "
                "At the end, provide brief feedback on their interview performance."
            )
            builder.set_category("Interview")
            builder.set_temperature(0.6)
            builder.set_voice("leo")
        
        elif template == AgentTemplate.CUSTOMER_SERVICE:
            builder.set_name("Customer Service Agent")
            builder.set_description(
                "Collect customer feedback and resolve issues. "
                "Gather information about customer problems and satisfaction."
            )
            builder.set_instructions(
                "You are a helpful customer service agent. Your goal is to:\n\n"
                "1. Greet the customer warmly\n"
                "2. Ask how you can help them today\n"
                "3. Gather details about their issue or feedback\n"
                "4. Ask follow-up questions to understand the problem\n"
                "5. Ask about their overall satisfaction (1-10 scale)\n"
                "6. Thank them for their time\n\n"
                "Be empathetic, professional, and helpful. "
                "Ask one question at a time and acknowledge each response."
            )
            builder.set_category("Customer Service")
            builder.set_temperature(0.7)
            builder.set_voice("leah")
        
        elif template == AgentTemplate.FEEDBACK_COLLECTOR:
            builder.set_name("Product Feedback Collector")
            builder.set_description(
                "Collect user feedback about products or services. "
                "Understand user experience and improvement suggestions."
            )
            builder.set_instructions(
                "You are collecting feedback about a product or service. "
                "Ask the following questions:\n\n"
                "1. What product or service are you providing feedback on?\n"
                "2. How long have you been using it?\n"
                "3. What do you like most about it?\n"
                "4. What frustrates you or could be improved?\n"
                "5. On a scale of 1-10, how likely are you to recommend it to a friend?\n"
                "6. Any other comments or suggestions?\n\n"
                "Be curious and encouraging. Ask follow-up questions if responses are vague."
            )
            builder.set_category("Feedback")
            builder.set_temperature(0.7)
        
        elif template == AgentTemplate.SURVEY:
            builder.set_name("General Survey Agent")
            builder.set_description(
                "Conduct surveys and collect structured data. "
                "Customizable for any survey needs."
            )
            builder.set_instructions(
                "You are conducting a survey. Ask questions one at a time and "
                "record the responses. Be neutral and professional. "
                "Acknowledge each response briefly before asking the next question.\n\n"
                "Customize these questions as needed:\n"
                "1. [Your first question]\n"
                "2. [Your second question]\n"
                "3. [Your third question]\n\n"
                "Thank the participant at the end."
            )
            builder.set_category("Survey")
            builder.set_temperature(0.5)
        
        return builder


def create_template_agent(template_name: str) -> Dict[str, Any]:
    """
    Create an agent from a template name.
    
    Args:
        template_name: Name of the template (e.g., 'startup_validator')
        
    Returns:
        Agent configuration dictionary
    """
    try:
        template = AgentTemplate(template_name)
        return AgentBuilder.from_template(template).build()
    except ValueError:
        raise ValueError(f"Unknown template: {template_name}")


def get_available_templates() -> list[Dict[str, str]]:
    """
    Get list of available agent templates.
    
    Returns:
        List of template dictionaries with name and description
    """
    templates = []
    for template in AgentTemplate:
        builder = AgentBuilder.from_template(template)
        config = builder.build()
        templates.append({
            "id": template.value,
            "name": config["name"],
            "description": config["description"],
            "category": config["category"],
        })
    return templates

