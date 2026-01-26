"""Custom Voice Model Provider for Groq STT and Orpheus TTS."""

from agents.voice import VoiceModelProvider, STTModel, TTSModel
from .groq_stt import GroqSTTModel
from .orpheus_tts import OrpheusTTSModel


class CustomVoiceModelProvider(VoiceModelProvider):
    """Voice model provider that uses Groq for STT and Orpheus TTS via LM Studio."""

    def __init__(
        self,
        groq_api_key: str,
        lm_studio_url: str,
        stt_model: str = "whisper-large-v3",
        tts_voice: str = "tara",
    ):
        """
        Initialize the custom voice model provider.

        Args:
            groq_api_key: Groq API key for STT
            lm_studio_url: LM Studio server URL (required, must be provided from settings)
            stt_model: STT model name
            tts_voice: Voice for Orpheus TTS
        """

        self.groq_api_key = groq_api_key
        self.stt_model_name = stt_model

        # Create instances
        self._stt = GroqSTTModel(api_key=groq_api_key, model=stt_model)
        self._tts = OrpheusTTSModel(base_url=lm_studio_url, voice=tts_voice)

    def get_stt_model(self, model_name: str | None) -> STTModel:
        """
        Get the speech-to-text model.

        Args:
            model_name: Model name (ignored, uses configured model)

        Returns:
            The Groq STT model
        """
        return self._stt

    def get_tts_model(self, model_name: str | None) -> TTSModel:
        """
        Get the text-to-speech model.

        Args:
            model_name: Model name (ignored, uses Orpheus TTS)

        Returns:
            The Orpheus TTS model
        """
        return self._tts
