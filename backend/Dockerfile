# Voice Agent Backend - Production image for VPS deployment
# Build from repo root:  docker build -f backend/Dockerfile .
FROM python:3.12-slim-bookworm

# Install system deps for audio (sounddevice/portaudio)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libportaudio2 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Create app user (non-root)
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

# Copy backend into /app/backend so "backend" package resolves with PYTHONPATH=/app
COPY backend /app/backend

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Switch to non-root user
USER appuser

EXPOSE 8000

# Production: no reload; bind to 0.0.0.0 for external access
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
