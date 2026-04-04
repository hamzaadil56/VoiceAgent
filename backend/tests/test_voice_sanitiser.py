"""Tests for voice STT sanitisation and save_answer single-call guard."""

from __future__ import annotations

import asyncio
import json
import uuid

import pytest
from agents.tool import ToolContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from v1.models import Base, Form, Organization, RespondentSession
from v1.services.agent_engine import FormSessionContext, save_answer
from v1.services.voice_workflow import _sanitise_transcription


@pytest.fixture
def voice_db():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    session = SessionLocal()
    try:
        org = Organization(id=str(uuid.uuid4()), name="Test Org")
        session.add(org)
        form = Form(
            id=str(uuid.uuid4()),
            org_id=org.id,
            title="Game form",
            slug="game-form-test",
            status="published",
            fields_schema=[
                {"name": "game_type", "required": True, "description": "Type of games"},
                {"name": "gaming_platform", "required": True, "description": "Platform"},
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
        yield session, form, rs, SessionLocal
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_sanitise_rejects_punctuation_only():
    assert _sanitise_transcription(".") is None
    assert _sanitise_transcription("..") is None
    assert _sanitise_transcription("...") is None
    assert _sanitise_transcription("!") is None
    assert _sanitise_transcription(". .") is None


def test_sanitise_accepts_short_real_answers():
    assert _sanitise_transcription("PC") == "PC"
    assert _sanitise_transcription("Sports") == "Sports"
    assert _sanitise_transcription("a") == "a"


def test_sanitise_rejects_empty_and_fillers():
    assert _sanitise_transcription("") is None
    assert _sanitise_transcription("   ") is None
    assert _sanitise_transcription("Thank you") is None
    assert _sanitise_transcription("okay") is None


def test_sanitise_rejects_prompt_bleed():
    assert _sanitise_transcription("voice interview stuff") is None
    assert _sanitise_transcription("Transcribe their actual spoken words") is None


def test_save_answer_second_call_rejected(voice_db):
    session, form, rs, _SessionLocal = voice_db
    ctx = FormSessionContext(
        db=session,
        respondent_session=rs,
        form=form,
        collected_answers={},
    )
    async def invoke(payload: dict) -> str:
        tctx = ToolContext(
            context=ctx,
            tool_name="save_answer",
            tool_call_id="test-call-1",
            tool_arguments=json.dumps(payload),
        )
        return await save_answer.on_invoke_tool(tctx, json.dumps(payload))

    r1 = asyncio.run(invoke({"field_name": "game_type", "value": "adventure"}))
    assert "Error" not in r1
    assert ctx.save_answer_called is True

    r2 = asyncio.run(invoke({"field_name": "gaming_platform", "value": "PC"}))
    assert "Error" in r2
    assert "Only one save_answer" in r2
