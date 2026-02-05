#!/usr/bin/env bash
# Backend build for deployment. Run with: bash build.sh (or ./build.sh if executable)
# Installs deps with uv if available, else pip install -r requirements.txt (e.g. on Vercel).

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Voice Agent Backend — Build"
echo ""

if command -v uv &> /dev/null; then
    echo "Using uv: $(uv --version)"
    uv sync
else
    echo "Using pip (uv not found)"
    pip install -r requirements.txt
fi
echo ""

echo "Verifying application import..."
if python -c "from main import app; print('App loaded:', getattr(app, 'title', 'Voice Agent API'))" 2>/dev/null; then
    echo "Build complete — app loads successfully"
else
    echo "Build finished but app import check failed (missing .env or runtime deps?)"
    exit 1
fi
echo ""
