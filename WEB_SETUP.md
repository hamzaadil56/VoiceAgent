# Web Application Setup Guide

## Quick Start

### Prerequisites

1. **Python 3.10+** with voiceagent package installed
2. **Node.js 18+** and npm
3. **ffmpeg** (for WebM to WAV conversion) - Optional but recommended
4. **LM Studio** running with Orpheus TTS model loaded
5. **Groq API Key** in `.env` file

### Backend Setup

1. Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

2. Make sure the voiceagent package is installed:

```bash
# From project root
pip install -e .
```

3. Start the backend server:

```bash
cd backend
python -m uvicorn backend.main:app --host localhost --port 8000 --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Install frontend dependencies:

```bash
cd frontend
npm install
```

2. Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Using the Startup Script

Alternatively, use the provided startup script:

```bash
./start_web.sh
```

This will start both backend and frontend servers.

## Features

-   **Real-time Voice Communication**: WebSocket-based bidirectional audio streaming
-   **Animated Visual Feedback**: Circle animation changes based on agent state
    -   Idle: Static circle
    -   Listening: Pulsing blue circle (user speaking)
    -   Processing: Rotating purple circle (agent thinking)
    -   Speaking: Animated green circle (agent speaking)
-   **Text Input Alternative**: Type messages and get voice responses
-   **Settings Panel**: Configure agent name, voice, temperature, and more
-   **Conversation History**: View past interactions

## Architecture

-   **Backend**: FastAPI with WebSocket support
-   **Frontend**: React + TypeScript + Tailwind CSS
-   **Communication**: WebSocket for real-time audio streaming
-   **Audio Format**: WebM from browser, converted to WAV for processing

## Troubleshooting

### WebM Conversion Issues

If you see errors about WebM conversion, install ffmpeg:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### CORS Errors

Make sure the backend CORS settings in `backend/config.py` include your frontend URL.

### Audio Not Playing

-   Check browser console for errors
-   Verify microphone permissions are granted
-   Ensure audio output device is working

### Connection Issues

-   Verify backend is running on port 8000
-   Check WebSocket URL in frontend (default: `ws://localhost:8000/ws`)
-   Ensure LM Studio is running with Orpheus model loaded
