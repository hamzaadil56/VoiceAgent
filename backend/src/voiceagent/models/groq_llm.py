"""Custom LLM model provider for Groq using LiteLLM."""

import warnings
from agents.extensions.models.litellm_model import LitellmModel

# Suppress Pydantic serialization warnings from LiteLLM
# These occur because LiteLLM responses don't perfectly match OpenAI's format
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")


def create_groq_model(
    api_key: str,
    model: str = "llama-3.3-70b-versatile",
) -> LitellmModel:
    """
    Create a Groq LLM model using LiteLLM.

    According to OpenAI Agents SDK docs, we can use any model via LiteLLM.
    Model settings like temperature and max_tokens are configured via
    the Agent's model_settings parameter, not the model constructor.

    Args:
        api_key: Groq API key
        model: Model name (e.g., llama-3.3-70b-versatile)

    Returns:
        LitellmModel configured for Groq
    """
    # LiteLLM uses "groq/" prefix for Groq models
    litellm_model = f"groq/{model}"

    return LitellmModel(
        model=litellm_model,
        api_key=api_key,
    )
