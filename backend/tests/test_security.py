"""Tests for security/auth utilities."""

import pytest
from v1.security import (
    create_access_token,
    create_public_session_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    hashed = hash_password("my_password")
    assert hashed != "my_password"
    assert verify_password("my_password", hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_access_token_roundtrip():
    token = create_access_token("user-123", extra={"org": "org-456"})
    claims = decode_token(token)
    assert claims["sub"] == "user-123"
    assert claims["type"] == "access"
    assert claims["org"] == "org-456"


def test_session_token_roundtrip():
    token = create_public_session_token("session-789")
    claims = decode_token(token)
    assert claims["sid"] == "session-789"
    assert claims["type"] == "public_session"


def test_invalid_token():
    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_token("garbage.token.here")
