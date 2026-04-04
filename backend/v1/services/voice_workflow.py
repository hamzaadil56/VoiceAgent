"""VoicePipeline workflow for agentic forms: DB-backed session + streamed LLM text."""

from __future__ import annotations

import logging
import re
from collections.abc import AsyncIterator, Callable
from typing import Any

from agents import Runner
from agents.voice import VoiceWorkflowBase
from sqlalchemy.orm import Session

from ..models import Form, Message, RespondentSession
from .agent_engine import (
    POLITE_FILLERS,
    FormSessionContext,
    _load_collected_answers,
    _load_history,
    build_form_agent,
)

logger = logging.getLogger(__name__)

# Whisper often returns "." / ".." on garbage audio; reject punctuation-only strings.
_PUNCT_ONLY_RE = re.compile(r"^[\s\W]+$")

PROMPT_BLEED_PHRASES = frozenset({
    "transcribe their actual spoken words",
    "if no speech is detected",
    "voice interview",
    "form questions",
    "return an empty string",
    "answering form questions",
})


def _is_only_filler(text: str) -> bool:
    """True if the transcription is just a polite filler, not a real answer."""
    normalised = text.strip().lower().rstrip(".!?,;:")
    return normalised in POLITE_FILLERS


def _sanitise_transcription(text: str) -> str | None:
    """Return None if transcription is invalid (empty, filler, or prompt-bleed). Else cleaned text."""
    t = text.strip()
    if not t:
        return None
    if _PUNCT_ONLY_RE.match(t):
        return None
    if _is_only_filler(t):
        return None
    lower = t.lower()
    for phrase in PROMPT_BLEED_PHRASES:
        if phrase in lower:
            return None
    return t


def _fallback_response(form: Form, collected: dict[str, str]) -> str:
    """Build a fallback question for the next missing required field."""
    required = [f["name"] for f in (form.fields_schema or []) if f.get("required", True)]
    missing = [f for f in required if f not in collected]
    if not missing:
        return "Thank you so much! All your responses have been recorded."
    next_field = missing[0]
    field_info = next(
        (f for f in (form.fields_schema or []) if f["name"] == next_field), {}
    )
    desc = field_info.get("description", next_field.replace("_", " "))
    return f"Could you tell me: {desc}?"


class FormAgentVoiceWorkflow(VoiceWorkflowBase):
    """Runs the form agent on each STT transcript; persists messages; yields text for TTS.

    Uses Runner.run (non-streaming) with max_turns=3. save_answer is limited to once per run
    via FormSessionContext.save_answer_called, so the model cannot fill multiple fields in one turn.
    """

    def __init__(
        self,
        db_factory: Callable[[], Session],
        session_id: str,
        form_id: str,
    ):
        self._db_factory = db_factory
        self.session_id = session_id
        self.form_id = form_id
        self.last_result: dict[str, Any] | None = None

    async def run(self, transcription: str) -> AsyncIterator[str]:
        db = self._db_factory()
        raw = (transcription or "").strip()
        logger.info("[VoiceWorkflow] STT (raw): %r  session=%s", raw, self.session_id)
        text = _sanitise_transcription(raw) or ""
        try:
            respondent_session = db.get(RespondentSession, self.session_id)
            form = db.get(Form, self.form_id)

            if not respondent_session or not form:
                msg = "Session or form not found."
                self.last_result = {
                    "transcription": raw,
                    "response": msg,
                    "state": "error",
                    "accepted": False,
                }
                yield msg
                return

            if respondent_session.status != "active":
                msg = "This session is no longer active."
                self.last_result = {
                    "transcription": raw,
                    "response": msg,
                    "state": respondent_session.status,
                    "accepted": False,
                }
                yield msg
                return

            if not text:
                logger.info(
                    "[VoiceWorkflow] Filler/bleed/empty STT (raw=%r) — re-prompting", raw
                )
                fresh = _load_collected_answers(db, self.session_id)
                msg = _fallback_response(form, fresh)
                self.last_result = {
                    # Omit junk from client chat (e.g. Whisper ".")
                    "transcription": text,
                    "response": msg,
                    "state": respondent_session.status,
                    "accepted": True,
                }
                yield msg
                return

            # ----------------------------------------------------------------
            # Build agent + context
            # ----------------------------------------------------------------
            collected = _load_collected_answers(db, self.session_id)
            voice_mode = getattr(respondent_session, "channel", None) == "voice"
            agent = build_form_agent(form, collected_answers=collected, voice_mode=voice_mode)
            context = FormSessionContext(
                db=db,
                respondent_session=respondent_session,
                form=form,
                collected_answers=collected,
            )

            # Persist user message AFTER loading history to avoid duplication.
            history = _load_history(db, self.session_id, max_messages=10)
            input_items = list(history)
            input_items.append({"role": "user", "content": text})
            db.add(Message(session_id=self.session_id, role="user", content=text))
            db.flush()

            # ----------------------------------------------------------------
            # Run agent — max_turns=3 leaves room if the model mixes text + tool in one step.
            # save_answer may run at most once per run (see FormSessionContext.save_answer_called).
            # ----------------------------------------------------------------
            response_text = ""
            try:
                result = await Runner.run(
                    starting_agent=agent,
                    input=input_items,
                    context=context,
                    max_turns=3,
                )
                response_text = (
                    str(result.final_output).strip() if result.final_output else ""
                )
                logger.info(
                    "[VoiceWorkflow] Agent response: %r  session=%s",
                    response_text[:200] if response_text else "",
                    self.session_id,
                )
            except Exception as exc:
                logger.exception("FormAgentVoiceWorkflow agent run failed: %s", exc)

            # ----------------------------------------------------------------
            # Fallback: if the agent produced no text, ask the next question.
            # ----------------------------------------------------------------
            if not response_text:
                db.refresh(respondent_session)
                fresh = _load_collected_answers(db, self.session_id)
                response_text = _fallback_response(form, fresh)
                logger.info(
                    "[VoiceWorkflow] Using fallback response: %r  session=%s",
                    response_text,
                    self.session_id,
                )

            yield response_text

            db.add(
                Message(
                    session_id=self.session_id,
                    role="assistant",
                    content=response_text,
                )
            )
            db.commit()

            db.refresh(respondent_session)
            self.last_result = {
                "transcription": text,
                "response": response_text,
                "state": respondent_session.status,
                "accepted": True,
            }
        finally:
            db.close()
