# Project knowledge

This file gives Codebuff context about your project: goals, commands, conventions, and gotchas.

## Overview
Real-time voice agent: browser-based frontend captures audio, streams it over WebSocket to a FastAPI backend that runs an STT → LLM → TTS pipeline, and streams PCM audio back.

## Quickstart
- **Backend setup:** `cd backend && uv sync` (use `uv sync --extra dev` for pytest/black/ruff)
- **Backend run:** `cd backend && uv run uvicorn main:app --host 0.0.0.0 --port 8000`
- **Frontend setup:** `cd frontend && npm install`
- **Frontend dev:** `cd frontend && npm run dev` (Vite on port 5173, proxies /api and /ws to backend)
- **Frontend build:** `cd frontend && npm run build` (runs tsc then vite build)
- **Frontend lint:** `cd frontend && npm run lint`

## Environment variables
Backend `.env` (in `backend/` directory):
- `GROQ_API_KEY` – Groq API key (STT, LLM, PlayAI TTS)
- Optional: `OPENAI_API_KEY` (only if you use OpenAI elsewhere), `HOST`, `PORT`, `RELOAD`, `LOG_LEVEL`

Frontend: `VITE_BACKEND_URL`, `VITE_WS_URL` (defaults to localhost:8000)

## Architecture
- **backend/** – FastAPI app (Python 3.10+, managed by `uv`)
  - `main.py` – App entrypoint, CORS, lifespan, routes
  - `config.py` – `BackendSettings` via pydantic-settings
  - `routes/api.py` – REST endpoints under `/api`
  - `routes/websocket.py` – WebSocket at `/ws` for real-time voice
  - `services/voice_service.py` – Wraps the voiceagent pipeline
  - `src/voiceagent/` – Core voice library (agent, audio, models, services)
  - `index.py` – Vercel entrypoint
- **frontend/** – React 18 + TypeScript + Vite + Tailwind CSS + Framer Motion
  - `src/components/` – UI components (VoiceBot, AnimatedCircle, Settings)
  - `src/hooks/` – React hooks (useAudio, useWebSocket, useServices)
  - `src/services/` – Audio/WebSocket/SilenceDetection service managers
  - `src/viewmodels/` – MVVM view models for VoiceBot
- **Data flow:** Browser mic → WebSocket (WebM/WAV) → FastAPI → OpenAI Agents SDK `VoicePipeline` (Groq STT → agent → Groq TTS) → PCM over WebSocket → Browser playback. Consumer forms use `FormAgentVoiceWorkflow` + same Groq voice stack.

## Deployment
- Backend: Docker image pushed to Docker Hub via GitHub Actions on push to `main`, deployed to VPS via SSH + docker compose
- Frontend: Deployed to Vercel (https://voice-agent-nine-beige.vercel.app)
- Vercel backend fallback uses `pip install -r requirements.txt --break-system-packages` (no uv)

## Conventions
- Backend package manager: **uv** (not pip locally)
- Frontend package manager: **npm**
- Python formatting: **black**, linting: **ruff**
- Frontend: MVVM pattern (viewmodels directory), service manager classes
- Tailwind for styling, Framer Motion for animations
- TypeScript strict mode

## Gotchas
- `backend/src/` is added to `sys.path` in `main.py` so `voiceagent` resolves as a top-level import
- Repo root is also on `sys.path` so `backend.*` imports work
- Vercel uses `requirements.txt` with CPU-only PyTorch (special `--extra-index-url`)
- CORS origins are hardcoded in `config.py` — update when adding new frontend URLs
- `uv sync` must be run from `backend/` directory (path dependency resolution)
