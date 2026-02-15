"""Ephemeral session store with optional Redis backend.

Used for:
- WebSocket connection tracking
- Audio chunk buffering during voice sessions
- Rate limiting state

Falls back to in-memory dict when Redis is unavailable.
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

# Optional Redis import
try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False


class SessionStore:
    """Key-value store with TTL, backed by Redis or in-memory dict."""

    def __init__(self, redis_url: str | None = None):
        self._redis = None
        redis_url = redis_url or os.getenv("REDIS_URL")

        if redis_url and HAS_REDIS:
            try:
                self._redis = redis.from_url(redis_url, decode_responses=True)
                self._redis.ping()
                logger.info("SessionStore using Redis at %s", redis_url)
            except Exception as exc:
                logger.warning("Redis connection failed (%s), using in-memory fallback", exc)
                self._redis = None

        if not self._redis:
            logger.info("SessionStore using in-memory fallback")

        # In-memory fallback
        self._memory: dict[str, tuple[Any, float | None]] = {}

    @property
    def is_redis(self) -> bool:
        return self._redis is not None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set a key with optional TTL in seconds."""
        if self._redis:
            serialized = json.dumps(value) if not isinstance(value, str) else value
            if ttl:
                self._redis.setex(key, ttl, serialized)
            else:
                self._redis.set(key, serialized)
        else:
            expires_at = (time.time() + ttl) if ttl else None
            self._memory[key] = (value, expires_at)

    def get(self, key: str) -> Any | None:
        """Get a value by key."""
        if self._redis:
            raw = self._redis.get(key)
            if raw is None:
                return None
            try:
                return json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                return raw
        else:
            entry = self._memory.get(key)
            if entry is None:
                return None
            value, expires_at = entry
            if expires_at and time.time() > expires_at:
                del self._memory[key]
                return None
            return value

    def delete(self, key: str) -> None:
        """Delete a key."""
        if self._redis:
            self._redis.delete(key)
        else:
            self._memory.pop(key, None)

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if self._redis:
            return bool(self._redis.exists(key))
        entry = self._memory.get(key)
        if entry is None:
            return False
        _, expires_at = entry
        if expires_at and time.time() > expires_at:
            del self._memory[key]
            return False
        return True

    # --- Convenience methods for session management ---

    def set_ws_connection(self, session_id: str, ws_id: str) -> None:
        """Track a WebSocket connection for a session."""
        self.set(f"ws:{session_id}", ws_id, ttl=3600)

    def get_ws_connection(self, session_id: str) -> str | None:
        """Get the WebSocket connection ID for a session."""
        return self.get(f"ws:{session_id}")

    def remove_ws_connection(self, session_id: str) -> None:
        """Remove the WebSocket connection tracking."""
        self.delete(f"ws:{session_id}")

    def append_audio_chunk(self, session_id: str, chunk: bytes) -> None:
        """Buffer an audio chunk for a voice session."""
        key = f"audio:{session_id}"
        existing = self.get(key) or []
        # Store as list of hex strings (JSON-safe)
        existing.append(chunk.hex())
        self.set(key, existing, ttl=300)  # 5 min TTL

    def get_audio_buffer(self, session_id: str) -> bytes:
        """Get combined audio buffer for a session."""
        key = f"audio:{session_id}"
        chunks = self.get(key) or []
        self.delete(key)
        return b"".join(bytes.fromhex(h) for h in chunks)

    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Simple sliding window rate limiter. Returns True if allowed."""
        rate_key = f"rate:{key}"
        now = time.time()

        if self._redis:
            pipe = self._redis.pipeline()
            pipe.zremrangebyscore(rate_key, 0, now - window_seconds)
            pipe.zadd(rate_key, {str(now): now})
            pipe.zcard(rate_key)
            pipe.expire(rate_key, window_seconds)
            _, _, count, _ = pipe.execute()
            return count <= max_requests
        else:
            entries = self.get(rate_key) or []
            entries = [t for t in entries if t > now - window_seconds]
            entries.append(now)
            self.set(rate_key, entries, ttl=window_seconds)
            return len(entries) <= max_requests


# Global instance (initialized on import)
session_store = SessionStore()
