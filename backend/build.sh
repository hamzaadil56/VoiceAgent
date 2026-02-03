#!/usr/bin/env bash
# Backend build script for cloud deployment.
# Installs all dependencies required to run the Voice Agent API.
# Run from the backend directory: ./build.sh
# Or from repo root: backend/build.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR"
REPO_ROOT="$(cd "$BACKEND_DIR/.." && pwd)"

echo "╔═══════════════════════════════════════════════════════╗"
echo "║           Voice Agent Backend — Build                 ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "Backend:  $BACKEND_DIR"
echo "Repo root: $REPO_ROOT"
echo ""

# Prefer uv if available, otherwise pip
USE_UV=false
if command -v uv &> /dev/null; then
    USE_UV=true
    echo "Using uv: $(uv --version)"
else
    echo "Using pip: $(pip --version 2>/dev/null || python3 -m pip --version)"
fi
echo ""

# 1) Install the voiceagent package from repo root (backend depends on it)
echo "📦 Installing voiceagent package from repo root..."
if [ "$USE_UV" = true ]; then
    uv pip install -e "$REPO_ROOT"
else
    pip install -e "$REPO_ROOT"
fi
echo "✅ voiceagent package installed"
echo ""

# 2) Install backend web dependencies (FastAPI, uvicorn, etc.)
echo "📦 Installing backend dependencies (requirements.txt)..."
if [ "$USE_UV" = true ]; then
    uv pip install -r "$BACKEND_DIR/requirements.txt"
else
    pip install -r "$BACKEND_DIR/requirements.txt"
fi
echo "✅ Backend requirements installed"
echo ""

# 3) Verify the app can be loaded
echo "🔍 Verifying application import..."
cd "$REPO_ROOT"
if python3 -c "
from backend.main import app
print('App loaded:', getattr(app, 'title', 'Voice Agent API'))
" 2>/dev/null; then
    echo "✅ Build complete — app loads successfully"
else
    echo "⚠️  Build finished but app import check failed (missing .env or runtime deps?)"
    exit 1
fi
echo ""
echo "Run the API from repo root with: python -m backend.main  (or uvicorn backend.main:app)"
