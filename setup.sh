#!/bin/bash

# VoiceAgent Setup Script
# This script automates the setup process

set -e

echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║           🎙️  VOICE AGENT SETUP                     ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Check for UV
echo "📦 Checking for UV package manager..."
if ! command -v uv &> /dev/null; then
    echo "❌ UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "✅ UV found: $(uv --version)"
fi

# Check Python version
echo ""
echo "🐍 Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python found: $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
uv venv

# Activate virtual environment
echo "✅ Virtual environment created"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
source .venv/bin/activate
uv pip install -e .

echo "✅ Dependencies installed"

# Setup .env file
echo ""
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << 'EOF'
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# OpenAI API Configuration (for TTS)
OPENAI_API_KEY=your_openai_api_key_here

# Voice Agent Configuration
STT_MODEL=whisper-large-v3
TTS_MODEL=tts-1
LLM_MODEL=llama-3.3-70b-versatile

# Audio Configuration
SAMPLE_RATE=16000
CHANNELS=1
CHUNK_SIZE=1024
RECORD_SECONDS=5
SILENCE_THRESHOLD=500
SILENCE_DURATION=2.0

# Agent Configuration
AGENT_NAME=VoiceAssistant
AGENT_INSTRUCTIONS=You are a helpful voice assistant. Keep your responses concise and natural for spoken conversation.
MAX_TOKENS=500
TEMPERATURE=0.7
EOF
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - GROQ_API_KEY: Get from https://console.groq.com/keys"
    echo "   - OPENAI_API_KEY: Get from https://platform.openai.com/api-keys"
else
    echo "✅ .env file already exists"
fi

# Audio dependencies check
echo ""
echo "🔊 Audio dependencies..."
echo "✅ Using sounddevice (no additional system dependencies needed)"

# Final message
echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║                                                       ║"
echo "║           ✅ SETUP COMPLETE!                         ║"
echo "║                                                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Activate virtual environment: source .venv/bin/activate"
echo "3. Run the voice agent: python main.py"
echo ""
echo "📚 Documentation:"
echo "   - Full Docs: See README.md"
echo "   - Examples: Run examples/*.py"
echo ""
echo "🎉 Happy voice chatting!"

