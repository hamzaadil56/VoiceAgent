"""Authentication and token utilities for Agentic Forms."""

from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "change-this-in-production")
JWT_ALG = "HS256"
ACCESS_TTL_MIN = int(os.getenv("ACCESS_TOKEN_TTL_MIN", "60"))
SESSION_TTL_HOURS = int(os.getenv("PUBLIC_SESSION_TTL_HOURS", "8"))
RESET_TOKEN_TTL_HOURS = 1


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TTL_MIN),
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def create_public_session_token(session_id: str) -> str:
    payload = {
        "sid": session_id,
        "type": "public_session",
        "exp": datetime.now(timezone.utc) + timedelta(hours=SESSION_TTL_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)


def generate_invite_token() -> str:
    return secrets.token_urlsafe(24)


def generate_api_key() -> tuple[str, str, str]:
    """Returns (raw_key, key_hash, prefix)."""
    raw = secrets.token_urlsafe(32)
    prefix = f"tf_{raw[:8]}"
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    return raw, key_hash, prefix


def hash_api_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()
