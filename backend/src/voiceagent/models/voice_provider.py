"""Voice model provider: Groq STT + Groq PlayAI TTS."""

from agents.voice import VoiceModelProvider, STTModel, TTSModel

from .groq_stt import GroqSTTModel
from .groq_tts import GroqTTSModel


class GroqVoiceModelProvider(VoiceModelProvider):
    """Maps SDK voice model names to Groq STT and Groq TTS implementations."""

    def __init__(
        self,
        groq_api_key: str,
        stt_model: str = "whisper-large-v3",
        tts_model: str = "playai-tts",
        tts_voice: str = "Fritz-PlayAI",
        *,
        tts_base_url: str = "https://api.groq.com/openai/v1",
    ):
        self.groq_api_key = groq_api_key
        self.stt_model_name = stt_model
        self.tts_model_name = tts_model
        self._stt = GroqSTTModel(api_key=groq_api_key, model=stt_model)
        self._tts = GroqTTSModel(
            api_key=groq_api_key,
            model=tts_model,
            voice=tts_voice,
            base_url=tts_base_url,
        )

    def get_stt_model(self, model_name: str | None) -> STTModel:
        return self._stt

    def get_tts_model(self, model_name: str | None) -> TTSModel:
        return self._tts


# Backward-compatible alias
CustomVoiceModelProvider = GroqVoiceModelProvider
