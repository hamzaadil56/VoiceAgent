"""Integration-style tests for FormAgentVoiceWorkflow (no live LLM for invalid STT paths)."""

from __future__ import annotations

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from v1.models import Base, Form, Organization, RespondentSession
from v1.services.voice_workflow import FormAgentVoiceWorkflow


@pytest.fixture
def voice_engine():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

    session = SessionLocal()
    org = Organization(id=str(uuid.uuid4()), name="Test Org")
    session.add(org)
    form = Form(
        id=str(uuid.uuid4()),
        org_id=org.id,
        title="Game form",
        slug="game-form-wf-test",
        status="published",
        fields_schema=[
            {"name": "game_type", "required": True, "description": "What type of games?"},
            {"name": "gaming_platform", "required": True, "description": "Which platform?"},
        ],
    )
    session.add(form)
    rs = RespondentSession(
        id=str(uuid.uuid4()),
        form_id=form.id,
        channel="voice",
        status="active",
    )
    session.add(rs)
    session.commit()
    session.close()

    yield engine, SessionLocal, form.id, rs.id


async def _consume_workflow(wf: FormAgentVoiceWorkflow, transcription: str) -> list[str]:
    chunks: list[str] = []
    async for part in wf.run(transcription):
        chunks.append(part)
    return chunks


def test_workflow_dot_transcription_reprompts_without_llm(voice_engine):
    _engine, SessionLocal, form_id, session_id = voice_engine

    def db_factory():
        return SessionLocal()

    wf = FormAgentVoiceWorkflow(db_factory, session_id=session_id, form_id=form_id)

    async def run():
        out = await _consume_workflow(wf, ".")
        return out

    out = asyncio.run(run())
    assert len(out) == 1
    assert "Could you tell me" in out[0]
    assert wf.last_result is not None
    assert wf.last_result["transcription"] == ""
    assert wf.last_result["accepted"] is True


def test_workflow_valid_transcription_calls_runner(voice_engine):
    _engine, SessionLocal, form_id, session_id = voice_engine

    def db_factory():
        return SessionLocal()

    wf = FormAgentVoiceWorkflow(db_factory, session_id=session_id, form_id=form_id)

    mock_result = MagicMock()
    mock_result.final_output = "Great — which platform do you use?"

    async def run():
        with patch("v1.services.voice_workflow.Runner.run", new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result
            return await _consume_workflow(wf, "I like adventure games")

    out = asyncio.run(run())
    assert out == ["Great — which platform do you use?"]
    assert wf.last_result["transcription"] == "I like adventure games"
    assert "platform" in wf.last_result["response"].lower()
