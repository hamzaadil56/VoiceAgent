# 🎙️ VoiceAgent

A **production-grade voice agent** built with OpenAI Agents SDK, Groq's AI models, and Orpheus TTS. Create AI-powered voice assistants that can hear, think, and speak naturally.

## ✨ Features

-   🎤 **Speech-to-Text**: Powered by Groq's Whisper models for fast, accurate transcription
-   🤖 **Intelligent Agent**: Uses Groq's Llama models via OpenAI Agents SDK for natural conversations
-   🔊 **Text-to-Speech**: Orpheus TTS via LM Studio for high-quality voice synthesis
-   🎭 **Multiple Voices**: 8 different voices (tara, leah, jess, leo, dan, mia, zac, zoe)
-   🔄 **Complete Pipeline**: Seamless audio → text → AI → speech → audio workflow
-   📦 **Modular Architecture**: Built on OpenAI Agents SDK with custom providers
-   ⚙️ **Configurable**: Environment-based configuration with sensible defaults
-   🎯 **Interactive Menu**: Menu-driven interface for all features
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
│    Agent    │  ◄── Llama-3.3-70b (Groq via LiteLLM)
│  (OpenAI)   │      OpenAI Agents SDK
└──────┬──────┘
       │
       ▼
┌─────────────┐
│TTS (Orpheus)│  ◄── lex-au/Orpheus-3b-FT-Q4_K_M.gguf
│ (LM Studio) │      Running on LM Studio
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
-   **LM Studio** with Orpheus TTS model
-   Microphone and speakers/headphones

### Setting up LM Studio

1. Download and install [LM Studio](https://lmstudio.ai/)
2. In LM Studio, search for and download: `lex-au/Orpheus-3b-FT-Q4_K_M.gguf`
3. Load the model in LM Studio
4. **IMPORTANT**: Start the local server (default: http://localhost:1234/v1)
    - The server must be running for TTS to work
    - Orpheus TTS uses the `/completions` endpoint (not `/chat/completions`)

Reference: [Orpheus TTS Local](https://github.com/isaiahbjork/orpheus-tts-local)

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

# Edit with your API key
nano .env
```

Add your API key:

```env
GROQ_API_KEY=your_groq_api_key_here
LM_STUDIO_URL=http://localhost:1234/v1
TTS_VOICE=tara
```

### 4. Run Your Voice Agent

```bash
python main.py
```

This launches the **interactive menu** where you can:

-   🎤 Start voice conversations
-   💬 Chat with text + voice responses
-   📝 Text-only chat mode
-   ⚙️ Configure agent settings
-   🎯 Quick test functionality
-   ℹ️ View system information

## 📖 Usage Examples

### Interactive Mode (Default)

```bash
python main.py
```

Provides a menu-driven interface with 7 options:

1. **Start Voice Conversation** - Full voice interaction
2. **Text Chat with Voice Response** - Type and hear responses
3. **Text-Only Chat** - Pure text mode
4. **Configure Agent Settings** - Customize behavior
5. **Quick Test** - Test the system
6. **System Information** - View configuration
7. **Exit** - Close the application

### Voice Conversation Mode

```bash
# Direct voice conversation (bypass menu)
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

## 🎨 Available Voices

Orpheus TTS supports 8 different voices:

-   **tara** (default) - Best overall voice for general use
-   **leah** - Clear female voice
-   **jess** - Friendly female voice
-   **leo** - Professional male voice
-   **dan** - Casual male voice
-   **mia** - Expressive female voice
-   **zac** - Energetic male voice
-   **zoe** - Calm female voice

Change voice in `.env`:

```env
TTS_VOICE=leo
```

Or in the interactive menu: Option 4 → Configure Agent Settings

## 🔧 Programmatic Usage

### Simple Usage

```python
import asyncio
from voiceagent import VoiceAgent, Settings

async def main():
    # Initialize with defaults
    agent = VoiceAgent()

    # Run conversation (voice)
    await agent.run_conversation(max_turns=3)

asyncio.run(main())
```

### Custom Agent

```python
from voiceagent import VoiceAgent, Settings

# Configure
settings = Settings()
settings.agent_name = "MyAssistant"
settings.agent_instructions = "You are a helpful coding assistant."
settings.temperature = 0.5
settings.tts_voice = "leo"

# Create agent
agent = VoiceAgent(settings)

# Use it
await agent.run_conversation()
```

### Using Custom Model Providers

```python
from agents import Agent, ModelSettings
from agents.voice import VoicePipeline, VoicePipelineConfig
from voiceagent.models import CustomVoiceModelProvider, create_groq_model

# Create LLM model
groq_model = create_groq_model(
    api_key="your_groq_api_key",
    model="llama-3.3-70b-versatile"
)

# Create agent
agent = Agent(
    name="CustomAgent",
    instructions="Your custom instructions",
    model=groq_model,
    model_settings=ModelSettings(temperature=0.7)
)

# Create voice provider
voice_provider = CustomVoiceModelProvider(
    groq_api_key="your_groq_api_key",
    lm_studio_url="http://localhost:1234/v1",
    tts_voice="tara"
)

# Create pipeline
config = VoicePipelineConfig(model_provider=voice_provider)
pipeline = VoicePipeline(workflow=agent, config=config)
```

## 📁 Project Structure

```
VoiceAgent/
├── src/voiceagent/
│   ├── __init__.py
│   ├── models/                 # Custom model providers
│   │   ├── groq_stt.py        # Groq Whisper STT
│   │   ├── orpheus_tts.py     # Orpheus TTS via LM Studio
│   │   ├── groq_llm.py        # Groq LLM via LiteLLM
│   │   └── voice_provider.py  # Custom VoiceModelProvider
│   ├── core/                  # Core orchestration
│   │   └── voice_agent.py     # Main VoiceAgent class
│   ├── config/                # Configuration
│   │   └── settings.py        # Environment settings
│   └── audio/                 # Audio utilities (if needed)
├── main.py                    # Interactive CLI interface
├── test_menu.py              # Menu testing script
├── pyproject.toml            # UV package config
├── requirements.txt          # Pip compatibility
└── README.md                 # This file
```

## ⚙️ Configuration

All settings can be configured via environment variables in `.env`:

### API Configuration

```env
GROQ_API_KEY=your_key                          # Required: Groq API key
LM_STUDIO_URL=http://localhost:1234/v1        # LM Studio server URL
TTS_VOICE=tara                                # Orpheus TTS voice
```

### Model Configuration

```env
STT_MODEL=whisper-large-v3                    # Speech-to-text model (Groq)
LLM_MODEL=llama-3.3-70b-versatile             # LLM for agent (Groq)
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

## 🐛 Troubleshooting

### No audio input detected

-   Check microphone permissions
-   Verify microphone is connected and working
-   Adjust `SILENCE_THRESHOLD` in `.env`

### LM Studio connection errors

-   Ensure LM Studio is running
-   Verify the local server is started (default: http://localhost:1234/v1)
-   Check that Orpheus model is loaded in LM Studio
-   Try accessing http://localhost:1234/v1/models in browser

### API errors

-   Verify Groq API key is correct in `.env`
-   Check API rate limits and quotas
-   Ensure internet connection is stable

### Audio playback issues

-   Check speaker/headphone connection
-   Verify system audio settings
-   Try different audio output devices
-   Check generated_audio/ folder for saved files

### Installation issues

```bash
# Reinstall dependencies
uv pip install --force-reinstall -e .

# If you have issues, try clearing UV cache
uv cache clean
```

## 🚀 Production Deployment

### Best Practices

1. **Security**: Store API keys securely (e.g., AWS Secrets Manager, HashiCorp Vault)
2. **Error Handling**: Implement retry logic for API calls with exponential backoff
3. **Monitoring**: Log conversations, errors, and performance metrics
4. **Rate Limiting**: Implement request throttling to avoid API limits
5. **Caching**: Cache TTS responses for common phrases
6. **Async**: All operations are async for better performance

### Scaling

-   Use message queues (RabbitMQ, Redis) for high traffic
-   Deploy behind load balancer (NGINX, HAProxy)
-   Consider streaming STT/TTS for lower latency
-   Implement session management for multiple users
-   Use Redis for distributed caching

## 🤝 Contributing

This is a production-ready template. Feel free to extend it:

-   Add more agent tools and functions
-   Integrate with databases for persistence
-   Add web interface (FastAPI + WebSockets)
-   Implement multi-language support
-   Add voice activity detection improvements
-   Create custom TTS voices

## 📝 License

MIT License - feel free to use in your projects!

## 🙏 Acknowledgments

-   **OpenAI Agents SDK**: Powerful agent framework
-   **Groq**: Fast Whisper STT and Llama LLM models
-   **LM Studio**: Local model runtime
-   **Orpheus TTS**: High-quality open-source TTS ([GitHub](https://github.com/isaiahbjork/orpheus-tts-local))
-   **Rich**: Beautiful terminal output

## 📞 Support

For issues and questions:

-   Run the test script: `python test_menu.py`
-   Check system info in interactive menu (Option 6)
-   Review configuration in `.env`
-   Check generated_audio/ folder for debugging

---

**Built with ❤️ using OpenAI Agents SDK, Groq, and Orpheus TTS**
