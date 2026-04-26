# TalkForms — Backend

FastAPI backend powering the TalkForms platform: agentic conversational forms completed via chat or voice, with an admin dashboard, JWT authentication, Groq-powered AI, and Alembic-managed SQL persistence.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Environment Configuration](#environment-configuration)
- [Installation](#installation)
- [Running the Server](#running-the-server)
- [Database Migrations](#database-migrations)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Docker](#docker)
- [Deployment Notes](#deployment-notes)

---

## Architecture Overview

```text
┌─────────────┐     HTTP / WebSocket     ┌──────────────────────────────────────┐
│   Frontend  │ ───────────────────────► │           FastAPI (main.py)          │
│  (React SPA)│                          │                                      │
└─────────────┘                          │  ┌────────────┐  ┌────────────────┐  │
                                         │  │ /api/*     │  │ /v1/*          │  │
                                         │  │ Legacy REST│  │ Agentic Forms  │  │
                                         │  └────────────┘  └────────────────┘  │
                                         │  ┌────────────┐  ┌────────────────┐  │
                                         │  │ /ws        │  │ /v1/public/    │  │
                                         │  │ Legacy WS  │  │ sessions/*/    │  │
                                         │  └────────────┘  │ voice (WS)     │  │
                                         │                  └────────────────┘  │
                                         └───────────────┬──────────────────────┘
                                                         │
                                          ┌──────────────┴──────────────┐
                                          │       Core Services         │
                                          │                             │
                                          │  VoiceService               │
                                          │  AgentEngine (OpenAI SDK)   │
                                          │  FormGenerator (LiteLLM)    │
                                          │  SQLAlchemy + Alembic DB    │
                                          └─────────────────────────────┘
```

On startup the application:

1. Runs pending Alembic migrations (falls back to `create_all` if Alembic is unavailable).
2. Seeds a default organization and admin account from environment variables.
3. Initialises `VoiceService` (Groq STT / LLM / TTS pipeline).

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| Web framework | FastAPI + Uvicorn |
| AI / LLM | OpenAI Agents SDK, LiteLLM → Groq (`llama-3.3-70b-versatile`) |
| Voice pipeline | `openai-agents[voice]`, Groq STT / TTS |
| Database ORM | SQLAlchemy 2 |
| Migrations | Alembic |
| Auth | JWT (`python-jose`), bcrypt (`passlib`) |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Config | Pydantic Settings (`.env` file) |

---

## Prerequisites

| Requirement | Version |
| --- | --- |
| Python | 3.10 or higher |
| [uv](https://docs.astral.sh/uv/) | latest |
| Groq API key | required for LLM, STT, TTS, and form generation |
| Database | SQLite (default, zero-config) or PostgreSQL |

Install `uv` if it is not already available:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Project Structure

```text
backend/
├── main.py                  # FastAPI app, lifespan, router registration
├── config.py                # BackendSettings (Pydantic Settings)
├── logging_config.py        # Structured logging setup
├── index.py                 # Vercel / serverless entrypoint
├── alembic.ini              # Alembic configuration
├── pyproject.toml           # Project metadata and dependencies (uv)
├── .env.example             # Template for environment variables
│
├── routes/
│   ├── api.py               # /api/* – legacy REST (health, settings, voices)
│   └── websocket.py         # /ws   – legacy voice WebSocket
│
├── services/
│   └── voice_service.py     # VoiceService wrapping the voiceagent pipeline
│
├── src/
│   └── voiceagent/          # Groq STT / LLM / TTS audio helpers
│
├── v1/                      # Agentic Forms API (all /v1/* routes)
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request / response schemas
│   ├── database.py          # Engine and session factory
│   ├── deps.py              # FastAPI dependency injection (auth, DB session)
│   ├── security.py          # JWT creation / verification, password hashing
│   ├── bootstrap.py         # init_db(): migrations + seed data
│   ├── session_store.py     # In-memory active session registry
│   │
│   ├── routes/
│   │   ├── auth.py          # /v1/auth/* – login, refresh, me
│   │   ├── forms.py         # /v1/orgs/:id/forms, /v1/forms/:id
│   │   ├── public.py        # /v1/public/* – consumer sessions, chat, voice
│   │   └── billing.py       # /v1/billing/* – Stripe webhook handling
│   │
│   ├── services/
│   │   ├── agent_engine.py  # OpenAI Agents SDK orchestration
│   │   ├── form_generator.py# AI form generation from natural language
│   │   ├── voice_workflow.py# Agentic voice session pipeline
│   │   ├── export_service.py# CSV export jobs
│   │   └── ...              # email, compliance, SSO, webhook helpers
│   │
│   └── migrations/
│       ├── env.py           # Alembic env (reads DATABASE_URL from env)
│       ├── script.py.mako   # Migration file template
│       └── versions/        # Versioned migration scripts
│
└── tests/                   # Pytest test suite
```

---

## Environment Configuration

Copy `.env.example` to `.env` inside the `backend/` directory and fill in the required values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
| --- | --- | --- |
| `GROQ_API_KEY` | Yes | Groq API key for LLM, STT, and TTS |
| `JWT_SECRET` | Yes | Secret used to sign all JWTs — **change before deploying** |
| `DATABASE_URL` | No | SQLAlchemy URL (default: `sqlite:///./agentic_forms.db`) |
| `AGENTIC_ADMIN_EMAIL` | No | Seed admin email (default: `admin@example.com`) |
| `AGENTIC_ADMIN_PASSWORD` | No | Seed admin password (default: `admin123`) |
| `AGENTIC_DEFAULT_ORG_NAME` | No | Seed organisation name (default: `Default Workspace`) |
| `ACCESS_TOKEN_TTL_MIN` | No | Admin JWT lifetime in minutes |
| `PUBLIC_SESSION_TTL_HOURS` | No | Public session JWT lifetime in hours |
| `OPENAI_API_KEY` | No | Required only if using OpenAI TTS |
| `STRIPE_SECRET_KEY` | No | Stripe billing integration |
| `RESEND_API_KEY` | No | Transactional email via Resend |
| `FRONTEND_URL` | No | Used in email links (default: `http://localhost:5173`) |
| `RELOAD` | No | Enable Uvicorn hot-reload (`true`/`false`) |

Server settings (host, port, CORS origins, log level) are configured via `BackendSettings` in [config.py](config.py) and can be overridden with matching environment variables.

---

## Installation

All commands are run from the **`backend/`** directory.

```bash
cd backend
uv sync
```

This creates a `.venv` and installs all runtime dependencies declared in `pyproject.toml`.

To also install development tools (pytest, black, ruff):

```bash
uv sync --extra dev
```

Activate the virtual environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

Once activated, `python` and `uvicorn` resolve from the venv directly. Alternatively, prefix every command with `uv run` to skip manual activation.

Verify the installation:

```bash
uv run python -c "from main import app; print('Installation OK')"
```

---

## Running the Server

Run the following command from the **`backend/`** directory:

```bash
cd backend
uv run uvicorn main:app --host localhost --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

| URL | Description |
| --- | --- |
| `http://localhost:8000/` | Service metadata and route index |
| `http://localhost:8000/docs` | Interactive Swagger UI |
| `http://localhost:8000/redoc` | ReDoc API documentation |

> **Note:** Run the server from `backend/` (not the repo root). The `main.py` entrypoint inserts `backend/src` onto `sys.path` so that `voiceagent` resolves correctly, but it relies on the working directory to locate `.env` and `alembic.ini`.

For production (no hot-reload):

```bash
uv run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

---

## Database Migrations

The project uses **Alembic** for schema migrations. All migration commands must be run from the **`backend/`** directory, where `alembic.ini` lives.

### Automatic migration on startup

`init_db()` in [v1/bootstrap.py](v1/bootstrap.py) runs `alembic upgrade head` automatically every time the server starts. No manual step is required for local development or standard deployments.

### Manual migration commands

```bash
cd backend
```

| Action | Command |
| --- | --- |
| Apply all pending migrations | `uv run alembic upgrade head` |
| Roll back one migration | `uv run alembic downgrade -1` |
| Roll back to a specific revision | `uv run alembic downgrade <revision_id>` |
| Show current revision | `uv run alembic current` |
| Show migration history | `uv run alembic history --verbose` |

### Creating a new migration

After modifying the SQLAlchemy models in [v1/models.py](v1/models.py), generate a migration automatically:

```bash
cd backend
uv run alembic revision --autogenerate -m "describe your change here"
```

This creates a new file under `v1/migrations/versions/`. Review the generated script before committing it — autogenerate does not detect every change (e.g. check constraints, custom types).

Apply the new migration immediately:

```bash
uv run alembic upgrade head
```

### Using PostgreSQL

Set `DATABASE_URL` in your `.env` file before running any migration commands. Alembic's `env.py` reads this variable at runtime and overrides the SQLite fallback in `alembic.ini`:

```env
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname
```

---

## API Reference

| Prefix | Auth | Description |
| --- | --- | --- |
| `GET /` | Public | Service metadata |
| `/api/*` | Public | Legacy: health, settings, voice list, Groq warm-up (`/api/spin`) |
| `WS /ws` | Public | Legacy voice WebSocket |
| `/v1/auth/*` | — | Admin login, token refresh, `GET /v1/auth/me` |
| `/v1/orgs/{org_id}/forms` | Admin JWT | List, create, and AI-generate forms |
| `/v1/orgs/{org_id}/dashboard` | Admin JWT | Organisation analytics |
| `/v1/forms/{form_id}` | Admin JWT | Get, update (draft only), publish, delete |
| `/v1/forms/{form_id}/submissions` | Admin JWT | List submissions and export to CSV |
| `/v1/public/f/{slug}/sessions` | Public | Create a respondent session for a published form |
| `/v1/public/sessions/{id}/message` | Session JWT | Send a chat message |
| `/v1/public/sessions/{id}/stream` | Session JWT | SSE streaming chat response |
| `/v1/public/sessions/{id}/messages` | Session JWT | Retrieve message history |
| `/v1/public/sessions/{id}/complete` | Session JWT | Manually mark a session complete |
| `WS /v1/public/sessions/{id}/voice` | Session JWT | Agentic voice WebSocket (STT → LLM → TTS) |

Full interactive documentation is available at `/docs` when the server is running.

---

## Testing

Run the test suite from the **`backend/`** directory:

```bash
cd backend
uv run pytest tests/ -v
```

---

## Docker

Build the image from the **repository root**:

```bash
docker buildx build -f backend/Dockerfile -t talkforms-backend:latest ./backend
```

Run the container:

```bash
docker run --env-file backend/.env -p 8000:8000 talkforms-backend:latest
```

Push to Docker Hub:

```bash
docker push hamzaadil/voiceagent-backend:latest
```

---

## Deployment Notes

- The repo includes a Vercel entrypoint at [index.py](index.py) that re-exports the FastAPI app. Set the `VERCEL_URL` and required secrets in the Vercel project environment.
- For any production deployment, ensure `JWT_SECRET` is set to a strong random value and `DATABASE_URL` points to a managed PostgreSQL instance.
- CORS origins are configured in [config.py](config.py) via `BackendSettings.cors_origins`. Add your production frontend URL there or override it with an environment variable.
- Alembic migrations run automatically on startup. For zero-downtime deployments, run `uv run alembic upgrade head` as a pre-deploy step before traffic is shifted.
