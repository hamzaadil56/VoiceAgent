"""Tests for the session store."""

import time
import pytest
from v1.session_store import SessionStore


@pytest.fixture
def store():
    """Create an in-memory session store."""
    return SessionStore(redis_url=None)


def test_set_and_get(store):
    store.set("key1", "value1")
    assert store.get("key1") == "value1"


def test_set_with_ttl_expires(store):
    store.set("key2", "value2", ttl=1)
    assert store.get("key2") == "value2"
    time.sleep(1.1)
    assert store.get("key2") is None


def test_delete(store):
    store.set("key3", "value3")
    store.delete("key3")
    assert store.get("key3") is None


def test_exists(store):
    assert store.exists("missing") is False
    store.set("present", "yes")
    assert store.exists("present") is True


def test_json_values(store):
    data = {"name": "John", "age": 30}
    store.set("json_key", data)
    assert store.get("json_key") == data


def test_ws_connection_tracking(store):
    store.set_ws_connection("session-1", "ws-abc")
    assert store.get_ws_connection("session-1") == "ws-abc"
    store.remove_ws_connection("session-1")
    assert store.get_ws_connection("session-1") is None


def test_audio_buffer(store):
    store.append_audio_chunk("session-2", b"\x00\x01\x02")
    store.append_audio_chunk("session-2", b"\x03\x04\x05")
    buffer = store.get_audio_buffer("session-2")
    assert buffer == b"\x00\x01\x02\x03\x04\x05"
    # Buffer should be cleared after get
    assert store.get_audio_buffer("session-2") == b""


def test_rate_limiter(store):
    for _ in range(5):
        assert store.check_rate_limit("client-1", max_requests=5, window_seconds=10) is True
    # 6th request should be denied
    assert store.check_rate_limit("client-1", max_requests=5, window_seconds=10) is False


def test_is_not_redis(store):
    assert store.is_redis is False
