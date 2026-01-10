# 🎙️ VoiceAgent

A **production-grade voice agent** built with Groq's high-performance AI models. Create AI-powered voice assistants that can see, hear, and speak naturally.

## ✨ Features

-   🎤 **Speech-to-Text**: Powered by Groq's Whisper models for fast, accurate transcription
-   🤖 **Intelligent Agent**: Uses Groq's Llama models for natural conversations
-   🔊 **Text-to-Speech**: Local Ollama model (legraphista/Orpheus) for voice synthesis
-   🔄 **Complete Pipeline**: Seamless audio → text → AI → speech → audio workflow
-   📦 **Modular Architecture**: Reusable components for custom integrations
-   ⚙️ **Configurable**: Environment-based configuration with sensible defaults
-   🚀 **Production-Ready**: Clean code, error handling, and logging

## 🏗️ Architecture

```
┌─────────────┐
│ Audio Input │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  STT (Groq) │  ◄── Whisper-large-v3
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Agent    │  ◄── Llama-3.3-70b (Groq)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│TTS (Ollama) │  ◄── legraphista/Orpheus:latest
└──────┬──────┘
       │
       ▼
┌─────────────┐
│Audio Output │
└─────────────┘
```

## 📋 Prerequisites

-   Python 3.10 or higher
-   UV package manager
-   **Groq API key** ([Get one here](https://console.groq.com))
-   **Ollama** installed locally with `legraphista/Orpheus:latest` model
-   Microphone and speakers/headphones

### Setting up Ollama

```bash
# Install Ollama from https://ollama.com/download

# Pull the Orpheus TTS model
ollama pull legraphista/Orpheus:latest

# Verify it's running
ollama list
```

## 🚀 Quick Start

### 1. Install UV Package Manager

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### 2. Clone and Setup

```bash
# Clone the repository (or download the code)
cd VoiceAgent

# Create virtual environment with UV
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### 3. Configure Environment

Create a `.env` file in the project root:

```bash
# Copy example
cp .env.example .env

# Edit with your API keys
nano .env
```

Add your API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run Your First Voice Agent

```bash
python main.py
```

This launches the interactive menu where you can:

-   Start voice conversations
-   Chat with text + voice responses
-   View conversation history
-   Customize agent instructions

## 📖 Usage Examples

### Interactive Mode (Default)

```bash
python main.py
```

Provides a menu-driven interface for all features.

### Voice Conversation Mode

```bash
# Unlimited conversation
python main.py --mode voice

# Limited to 5 turns
python main.py --mode voice --turns 5
```

### Text Mode

```bash
# Text input with voice response
python main.py --mode text --message "Hello, how are you?"

# Text only (no voice)
python main.py --mode text --message "What's the weather?" --no-voice-response
```

### Custom Instructions

```bash
python main.py --instructions "You are a pirate captain. Speak like a pirate!"
```

## 🔧 Programmatic Usage

### Simple Usage

```python
from voiceagent import VoiceAgent

# Initialize
agent = VoiceAgent()

# Run conversation (voice)
agent.run_conversation(max_turns=3)

# Text chat with voice response
response = agent.chat_text("Hello!", speak_response=True)
```

### Custom Agent

```python
from voiceagent import VoiceAgent, Settings

# Configure
settings = Settings()
settings.agent_name = "MyAssistant"
settings.agent_instructions = "You are a helpful coding assistant."
settings.temperature = 0.5

# Create agent
agent = VoiceAgent(settings)

# Use it
agent.run_conversation()
```

### Using Components Separately

```python
from voiceagent.services import SpeechToTextService, TextToSpeechService
from voiceagent.agent import VoiceAssistantAgent
from voiceagent.audio import AudioRecorder, AudioPlayer
from voiceagent.config import Settings

settings = Settings()

# Initialize components
recorder = AudioRecorder()
stt = SpeechToTextService(api_key=settings.groq_api_key)
agent = VoiceAssistantAgent(groq_api_key=settings.groq_api_key)
tts = TextToSpeechService(api_key=settings.groq_api_key)
player = AudioPlayer()

# Build custom pipeline
audio = recorder.record()
text = stt.transcribe(audio)
response = agent.chat(text)
audio_response = tts.synthesize(response)
player.play(audio_response)
```

## 📁 Project Structure

```
VoiceAgent/
├── src/voiceagent/
│   ├── __init__.py
│   ├── audio/              # Audio recording and playback
│   │   ├── recorder.py     # Voice activity detection
│   │   └── player.py       # Audio playback
│   ├── services/           # External API services
│   │   ├── stt_service.py  # Groq Whisper STT
│   │   └── tts_service.py  # TTS service
│   ├── agent/              # AI Agent logic
│   │   └── voice_assistant_agent.py
│   ├── core/               # Main orchestrator
│   │   └── voice_agent.py  # Pipeline manager
│   └── config/             # Configuration
│       └── settings.py     # Environment settings
├── examples/               # Usage examples
│   ├── simple_usage.py
│   ├── custom_agent_example.py
│   └── programmatic_usage.py
├── main.py                 # CLI entry point
├── pyproject.toml          # UV package config
└── README.md              # This file
```

## ⚙️ Configuration

All settings can be configured via environment variables in `.env`:

### API Configuration

```env
GROQ_API_KEY=your_key        # Required: Groq API key
```

### Model Configuration

```env
STT_MODEL=whisper-large-v3                         # Speech-to-text model (Groq)
TTS_MODEL=legraphista/Orpheus:latest               # Text-to-speech model (Local Ollama)
LLM_MODEL=llama-3.3-70b-versatile                  # LLM for agent (Groq)
OLLAMA_HOST=http://localhost:11434                 # Ollama server URL
```

### Audio Configuration

```env
SAMPLE_RATE=16000           # Audio sample rate (Hz)
CHANNELS=1                  # Audio channels
CHUNK_SIZE=1024            # Recording chunk size
SILENCE_THRESHOLD=500      # Silence detection threshold
SILENCE_DURATION=2.0       # Silence duration to stop (seconds)
```

### Agent Configuration

```env
AGENT_NAME=VoiceAssistant
AGENT_INSTRUCTIONS="You are a helpful voice assistant..."
MAX_TOKENS=500             # Max response length
TEMPERATURE=0.7            # Creativity (0.0-1.0)
```

## 🎯 Use Cases

-   **Customer Support**: 24/7 voice-based customer service
-   **Personal Assistant**: Schedule management, reminders, tasks
-   **Education**: Language tutors, study companions
-   **Healthcare**: Patient intake, symptom checking
-   **Smart Home**: Voice control for IoT devices
-   **Gaming**: Interactive NPCs with voice
-   **Accessibility**: Voice interfaces for visually impaired users

## 🔍 Examples Directory

Run the included examples:

```bash
# Simple usage demo
python examples/simple_usage.py

# Domain-specific agents (fitness coach, language tutor, etc.)
python examples/custom_agent_example.py

# Component-level usage
python examples/programmatic_usage.py
```

## 🐛 Troubleshooting

### No audio input detected

-   Check microphone permissions
-   Verify microphone is connected and working
-   Adjust `SILENCE_THRESHOLD` in `.env`

### API errors

-   Verify API keys are correct in `.env`
-   Check API rate limits and quotas
-   Ensure internet connection is stable

### Audio playback issues

-   Check speaker/headphone connection
-   Verify system audio settings
-   Try different audio output devices

### Installation issues

```bash
# Reinstall dependencies
uv pip install --force-reinstall -e .

# If you have issues, try clearing UV cache
uv cache clean
```

## 🚀 Production Deployment

### Best Practices

1. **Security**: Store API keys securely (e.g., AWS Secrets Manager)
2. **Error Handling**: Implement retry logic for API calls
3. **Monitoring**: Log conversations and errors
4. **Rate Limiting**: Implement request throttling
5. **Caching**: Cache TTS responses for common phrases
6. **Async**: Use async/await for better performance

### Scaling

-   Use message queues (RabbitMQ, Redis) for high traffic
-   Deploy behind load balancer
-   Consider streaming STT/TTS for lower latency
-   Implement session management for multiple users

## 🤝 Contributing

This is a production-ready template. Feel free to extend it:

-   Add more agent tools and functions
-   Integrate with databases for persistence
-   Add web interface (FastAPI + WebSockets)
-   Implement multi-language support
-   Add voice activity detection improvements

## 📝 License

MIT License - feel free to use in your projects!

## 🙏 Acknowledgments

-   **Groq**: Fast Whisper STT and Llama LLM models
-   **Ollama**: Local LLM runtime for Orpheus TTS
-   **legraphista/Orpheus**: Open-source TTS model
-   **Rich**: Beautiful terminal output

## 📞 Support

For issues and questions:

-   Check the examples directory
-   Review configuration in `.env`
-   Test individual components separately

---

**Built with ❤️ using Groq + Ollama**
