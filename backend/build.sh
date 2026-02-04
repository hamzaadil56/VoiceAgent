#!/usr/bin/env bash
# Backend build for deployment. Run from repo root as ./build.sh or from backend as ./build.sh
# Installs all dependencies into backend/.venv using uv.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR"
cd "$BACKEND_DIR"

echo "Voice Agent Backend — Build (uv)"
echo "Backend dir: $BACKEND_DIR"
echo ""

if ! command -v uv &> /dev/null; then
    echo "uv is required. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo "Using uv: $(uv --version)"
echo ""

echo "Installing dependencies (uv sync)..."
uv sync
echo ""

echo "Verifying application import..."
if uv run python -c "from main import app; print('App loaded:', getattr(app, 'title', 'Voice Agent API'))" 2>/dev/null; then
    echo "Build complete — app loads successfully"
else
    echo "Build finished but app import check failed (missing .env or runtime deps?)"
    exit 1
fi
echo ""
echo "Run from backend dir: uv run uvicorn main:app --host 0.0.0.0 --port 8000"
