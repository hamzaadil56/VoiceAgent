# 🎙️ VoiceAgent

A **production-grade voice agent platform** with multiple interfaces - CLI and Web. Built with OpenAI Agents SDK, Groq's AI models, and Orpheus TTS. Create AI-powered voice assistants that can hear, think, and speak naturally.

## ✨ Features

-   🎤 **Speech-to-Text**: Powered by Groq's Whisper models for fast, accurate transcription
-   🤖 **Intelligent Agent**: Uses Groq's Llama models via OpenAI Agents SDK for natural conversations
-   🔊 **Text-to-Speech**: Orpheus TTS via LM Studio for high-quality voice synthesis
-   🎭 **Multiple Voices**: 8 different voices (tara, leah, jess, leo, dan, mia, zac, zoe)
-   🔄 **Complete Pipeline**: Seamless audio → text → AI → speech → audio workflow
-   📦 **Multiple Interfaces**: CLI menu-driven interface and modern Web UI with WebSocket support
-   ⚙️ **Configurable**: Environment-based configuration with sensible defaults
-   🚀 **Production-Ready**: Clean code, error handling, and logging

## 🏗️ Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interfaces                          │
├─────────────────────────────┬───────────────────────────────────┤
│      CLI Interface          │      Web Application              │
│   (Python Menu-Driven)      │   (React + TypeScript + Vite)     │
└──────────────┬──────────────┴──────────────┬────────────────────┘
               │                              │
               │                              │ WebSocket (WS)
               │                              │ REST API (/api)
               ▼                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Backend Services                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            FastAPI Backend (Python)                      │   │
│  │  - REST API endpoints (/api/health, /api/settings)      │   │
│  │  - WebSocket server (/ws) for real-time communication    │   │
│  │  - VoiceService wrapper for VoiceAgent integration       │   │
│  └───────────────────────┬──────────────────────────────────┘   │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Core Voice Agent Library                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            OpenAI Agents SDK                             │   │
│  │  - VoicePipeline for audio processing                    │   │
│  │  - SingleAgentVoiceWorkflow                              │   │
│  │  - CustomVoiceModelProvider                              │   │
│  └───────────┬──────────────────────────────┬────────────────┘   │
└──────────────┼──────────────────────────────┼────────────────────┘
               │                              │
       ┌───────▼───────┐            ┌─────────▼─────────┐
       │   STT (Groq)  │            │   LLM (Groq)      │
       │  Whisper-v3   │            │  Llama-3.3-70b    │
       └───────────────┘            └───────────────────┘
               │                              │
               │                              │
       ┌───────▼──────────────────────────────▼─────────┐
       │            TTS (Orpheus via LM Studio)         │
       │  - SNAC decoder for audio generation           │
       │  - Local LM Studio server (port 1234)          │
       └────────────────────────────────────────────────┘
```

### Pipeline Flow

```
┌─────────────┐
│ Audio Input │  (Microphone / Web Browser)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  STT (Groq) │  ◄── whisper-large-v3
│  Transcribe │
└──────┬──────┘
       │ (text)
       ▼
┌─────────────┐
│    Agent    │  ◄── llama-3.3-70b-versatile
│  (OpenAI)   │      OpenAI Agents SDK
│  Process    │
└──────┬──────┘
       │ (text response)
       ▼
┌─────────────┐
│TTS (Orpheus)│  ◄── lex-au/Orpheus-3b-FT-Q4_K_M.gguf
│ (LM Studio) │      SNAC Decoder
└──────┬──────┘
       │ (audio)
       ▼
┌─────────────┐
│Audio Output │  (Speakers / Web Browser)
└─────────────┘
```

## 🛠️ Tech Stack

### Backend

-   **Python 3.10+** - Core language
-   **FastAPI** - Modern, fast web framework for building APIs
-   **Uvicorn** - ASGI server for FastAPI
-   **WebSockets** - Real-time bidirectional communication
-   **Pydantic** - Data validation using Python type annotations
-   **Rich** - Terminal formatting library

### Frontend

-   **React 18** - UI library
-   **TypeScript** - Type-safe JavaScript
-   **Vite** - Fast build tool and dev server
-   **TailwindCSS** - Utility-first CSS framework
-   **WebSocket API** - Browser WebSocket client

### AI & Voice Processing

-   **OpenAI Agents SDK** - Agent framework and voice pipeline
-   **Groq** - Fast inference for STT (Whisper) and LLM (Llama)
-   **LM Studio** - Local model runtime for TTS
-   **Orpheus TTS** - High-quality open-source text-to-speech model
-   **SNAC Decoder** - Audio generation decoder for Orpheus

### Audio Processing

-   **sounddevice** - Audio I/O library (Python)
-   **soundfile** - Audio file I/O library
-   **numpy** - Numerical computing
-   **scipy** - Scientific computing (signal processing)

### Build & Package Management

-   **UV** - Fast Python package installer and resolver
-   **npm** - JavaScript package manager
-   **Hatchling** - Python build backend

## 📋 Prerequisites

-   **Python 3.10 or higher**
-   **Node.js 18+ and npm** (for web interface)
-   **UV package manager** (recommended) or pip
-   **Groq API key** ([Get one here](https://console.groq.com))
-   **LM Studio** with Orpheus TTS model installed
-   **Microphone and speakers/headphones**
-   **ffmpeg** (optional, for WebM conversion in web interface)

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
# Clone the repository
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
# Copy example (if exists)
cp .env.example .env

# Edit with your API key
nano .env
```

Add your configuration:

```env
GROQ_API_KEY=your_groq_api_key_here
LM_STUDIO_URL=http://localhost:1234/v1
TTS_VOICE=tara
```

### 4. Run CLI Interface

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

### 5. Run Web Application

```bash
# Start both backend and frontend
./start_web.sh

# Or manually:
# Terminal 1 - Backend
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend
npm install  # First time only
npm run dev
```

Access the web interface at: **http://localhost:5173**

Backend API available at: **http://localhost:8000**

## 👤 User Journey

### CLI Interface Journey

1. **Launch Application**: Run `python main.py` from terminal
2. **Main Menu**: Choose from 7 options:
    - Voice conversation (full audio interaction)
    - Text chat with voice response
    - Text-only chat
    - Configure settings
    - Quick test
    - System info
    - Exit
3. **Voice Conversation**:
    - System records audio (5 seconds default)
    - Audio sent to Groq STT for transcription
    - Text processed by Llama LLM via OpenAI Agents SDK
    - Response synthesized by Orpheus TTS via LM Studio
    - Audio played through speakers
    - Conversation continues until user exits
4. **Text Chat**: Type messages, receive voice responses
5. **Settings**: Configure voice, temperature, max tokens, etc.

### Web Interface Journey

1. **Access Web App**: Open browser to `http://localhost:5173`
2. **Initial Connection**: WebSocket automatically connects to backend
3. **Voice Interaction**:
    - Click the animated circle to start recording
    - Speak into microphone (browser captures audio)
    - Click circle again or "Stop & Send" button
    - Audio chunks sent via WebSocket to backend
    - Backend processes through Voice Agent pipeline
    - Transcription displayed in conversation history
    - Audio response streamed back and played
    - System returns to idle state
4. **Text Interaction**: Type message in input field, press Send
5. **Settings**: Click Settings tab to configure agent behavior
6. **Real-time Updates**: State changes reflected via WebSocket (listening, processing, speaking)

### Audio Flow (Web)

```
Browser Microphone
    ↓
Web Audio API (MediaRecorder)
    ↓
Base64 Encoded Chunks
    ↓
WebSocket → Backend
    ↓
VoiceService.process_audio_chunk()
    ↓
VoiceAgent.process_voice_input()
    ↓
Pipeline: STT → Agent → TTS
    ↓
Audio Response Streamed
    ↓
WebSocket → Browser
    ↓
AudioContext.playPCM()
    ↓
Speakers
```

### Audio Format Details

The web interface uses **raw PCM audio format** for consistent playback:

-   **Input Processing**: `process_audio_chunk()` accepts audio chunks (WebM or WAV) from the browser, converts them to numpy arrays, and processes through the voice agent pipeline
-   **Output Format**: Both `process_audio_chunk()` and `process_text_message()` return **raw PCM data** (16-bit, mono, 24kHz) in **4KB chunks** for streaming
-   **Format Consistency**: Standardized audio format ensures reliable playback across different browsers and audio contexts
-   **Streaming**: Audio is streamed in chunks via WebSocket for low-latency, real-time playback

## 📁 Project Structure

```
VoiceAgent/
├── src/voiceagent/              # Core Voice Agent library
│   ├── __init__.py
│   ├── core/
│   │   └── voice_agent.py       # Main VoiceAgent class
│   ├── models/                  # Model providers
│   │   ├── groq_stt.py          # Groq Whisper STT
│   │   ├── orpheus_tts.py       # Orpheus TTS via LM Studio
│   │   ├── groq_llm.py          # Groq LLM via LiteLLM
│   │   └── voice_provider.py    # Custom VoiceModelProvider
│   ├── config/
│   │   └── settings.py          # Configuration settings
│   └── audio/                   # Audio utilities
│
├── backend/                     # FastAPI web backend
│   ├── main.py                  # FastAPI application
│   ├── config.py                # Backend configuration
│   ├── routes/
│   │   ├── api.py               # REST API endpoints
│   │   └── websocket.py         # WebSocket handler
│   └── services/
│       └── voice_service.py     # Voice service wrapper
│
├── frontend/                    # React frontend
│   ├── src/
│   │   ├── App.tsx              # Main app component
│   │   ├── components/
│   │   │   ├── VoiceBot.tsx     # Voice interaction component
│   │   │   ├── Settings.tsx     # Settings component
│   │   │   └── AnimatedCircle.tsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts  # WebSocket hook
│   │   │   └── useAudio.ts      # Audio recording/playback hook
│   │   └── utils/
│   │       ├── audioRecorder.ts
│   │       └── audioPlayer.ts
│   └── package.json
│
├── main.py                      # CLI interface entry point
├── examples/                    # Usage examples
├── pyproject.toml               # UV package config
├── requirements.txt             # Pip compatibility
├── Makefile                     # Build commands
└── start_web.sh                 # Web app startup script
```

## ⚙️ Configuration

All settings can be configured via environment variables in `.env`:

### API Configuration

```env
GROQ_API_KEY=your_key                    # Required: Groq API key
LM_STUDIO_URL=http://localhost:1234/v1   # LM Studio server URL
TTS_VOICE=tara                           # Orpheus TTS voice
```

### Model Configuration

```env
STT_MODEL=whisper-large-v3               # Speech-to-text model (Groq)
LLM_MODEL=llama-3.3-70b-versatile        # LLM for agent (Groq)
```

### Agent Configuration

```env
AGENT_NAME=VoiceAssistant
AGENT_INSTRUCTIONS="You are a helpful voice assistant..."
MAX_TOKENS=500                           # Max response length
TEMPERATURE=0.7                          # Creativity (0.0-1.0)
```

### Audio Configuration

```env
SAMPLE_RATE=24000        # Audio sample rate (Hz)
CHANNELS=1               # Audio channels
CHUNK_SIZE=1024          # Recording chunk size
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

Change voice in `.env` or via Settings UI in web interface.

## 📖 Usage Examples

### CLI Interface

```bash
# Interactive menu (default)
python main.py

# Direct voice conversation
python main.py --mode voice --turns 5

# Text mode
python main.py --mode text --message "Hello, how are you?"

# Custom instructions
python main.py --instructions "You are a pirate captain!"
```

### Programmatic Usage

```python
import asyncio
from voiceagent import VoiceAgent

async def main():
    agent = VoiceAgent()
    await agent.run_conversation(max_turns=3)

asyncio.run(main())
```

## 🐛 Troubleshooting

### No audio input detected

-   Check microphone permissions
-   Verify microphone is connected and working
-   Adjust `SILENCE_THRESHOLD` in `.env`

### LM Studio connection errors

-   Ensure LM Studio is running
-   Verify local server is started (http://localhost:1234/v1)
-   Check that Orpheus model is loaded
-   Try accessing http://localhost:1234/v1/models in browser

### API errors

-   Verify Groq API key is correct in `.env`
-   Check API rate limits and quotas
-   Ensure internet connection is stable

### Web interface issues

-   Check browser console for errors
-   Verify WebSocket connection (should see "Connected" status)
-   Ensure backend is running on port 8000
-   Check CORS settings in backend/config.py

### Installation issues

```bash
# Reinstall dependencies
uv pip install --force-reinstall -e .

# Clear UV cache
uv cache clean

# Frontend dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 🚀 Production Deployment

### Best Practices

1. **Security**: Store API keys securely (AWS Secrets Manager, HashiCorp Vault)
2. **Error Handling**: Implement retry logic with exponential backoff
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
-   Add multi-language support
-   Improve voice activity detection
-   Create custom TTS voices
-   Add authentication and user management

## 📝 License

MIT License - feel free to use in your projects!

## 🙏 Acknowledgments

-   **OpenAI Agents SDK** - Powerful agent framework
-   **Groq** - Fast Whisper STT and Llama LLM models
-   **LM Studio** - Local model runtime
-   **Orpheus TTS** - High-quality open-source TTS ([GitHub](https://github.com/isaiahbjork/orpheus-tts-local))
-   **Rich** - Beautiful terminal output

---

**Built with ❤️ using OpenAI Agents SDK, Groq, and Orpheus TTS**
