# Voice Agent Backend

FastAPI backend for the Voice Agent web interface. Provides REST API and WebSocket for real-time voice interaction using the shared `voiceagent` package (STT, LLM, TTS).

## Prerequisites

-   Python 3.10+
-   [uv](https://docs.astral.sh/uv/) (package manager)

Install uv if needed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Setup

1. Clone the repository (backend must live inside the repo so the `voiceagent` path dependency resolves).

2. From the **backend** directory, create the virtual environment and install dependencies:

    ```bash
    cd backend
    uv sync
    ```

    For development tools (pytest, black, ruff):

    ```bash
    uv sync --extra dev
    ```

3. Environment variables: place a `.env` file in the **backend** directory (or ensure the process runs with the correct working directory so `.env` is found). Required for the voice pipeline:

    - `GROQ_API_KEY` – Groq API key (STT/LLM)
    - `OPENAI_API_KEY` – OpenAI API key (TTS, if used)
    - Optional: `HOST`, `PORT`, `RELOAD`; for CORS, configure as needed (see `BackendSettings` in `config.py`).

## Architecture

-   **FastAPI** app with lifespan startup/shutdown.
-   **REST** under `/api`: health, settings, spin (TTS wake), etc.
-   **WebSocket** at `/ws`: real-time voice; client sends audio (WebM/WAV), receives PCM stream and transcripts.
-   **VoiceService** wraps the root **voiceagent** package: `VoiceAgent` (OpenAI Agents SDK voice pipeline) for STT → LLM → TTS. Audio is converted and streamed as PCM to the frontend.

```mermaid
flowchart LR
  Client[Frontend]
  FastAPI[FastAPI]
  VoiceService[VoiceService]
  VoiceAgent[voiceagent]
  Client -->|HTTP/WS| FastAPI
  FastAPI --> VoiceService
  VoiceService --> VoiceAgent
  VoiceAgent -->|STT/LLM/TTS| VoiceService
```

## Build and run (deployment)

**Build** (install all dependencies into `backend/.venv`):

```bash
cd backend
uv sync
```

Optional verification:

```bash
uv run python -c "from main import app; print('OK')"
```

**Run** the API (from the **backend** directory):

```bash
cd backend
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

Or use the default host/port from config:

```bash
uv run uvicorn main:app --host 0.0.0.0
```

To use a port from the environment (e.g. in cloud):

```bash
uv run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Alternative: run the app module directly (same effect as above):

```bash
uv run python main.py
```

**Deployment layout:** The voice agent library is source-only at `backend/src/voiceagent/` and uses the backend venv for all packages. There is a single `backend/pyproject.toml` and uv is the only package manager for the backend. Deploy with the full repo; run `uv sync` only in `backend/`.
