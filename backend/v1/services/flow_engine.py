"""Deterministic graph engine with lightweight personalization."""

from __future__ import annotations

import re
from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Form, FormGraphEdge, FormGraphNode, FormVersion, RespondentSession, Answer, Submission, Message


class FlowResult(dict):
    pass


def _personalize(prompt: str, persona: str) -> str:
    persona = (persona or "").strip()
    if not persona:
        return prompt
    return f"{prompt}\n\nTone: {persona}."


def _validate_answer(node: FormGraphNode, text: str) -> tuple[bool, str | None]:
    rules = node.validation_json or {}
    normalized = (text or "").strip()

    if node.required and not normalized:
        return False, "This question is required. Please provide an answer."

    expected_type = rules.get("type")
    if expected_type == "number":
        try:
            value = float(normalized)
        except ValueError:
            return False, "Please provide a valid number."
        min_value = rules.get("min")
        max_value = rules.get("max")
        if min_value is not None and value < float(min_value):
            return False, f"Value should be at least {min_value}."
        if max_value is not None and value > float(max_value):
            return False, f"Value should be at most {max_value}."

    pattern = rules.get("regex")
    if pattern and normalized and not re.match(pattern, normalized):
        return False, "The answer format is not valid. Please try again."

    enum = rules.get("enum")
    if enum and normalized.lower() not in {str(v).lower() for v in enum}:
        return False, f"Please choose one of: {', '.join(map(str, enum))}."

    return True, None


def _edge_matches(condition: dict[str, Any] | None, answer: str) -> bool:
    if not condition:
        return True
    equals = condition.get("equals")
    if equals is not None:
        return answer.strip().lower() == str(equals).strip().lower()
    contains = condition.get("contains")
    if contains is not None:
        return str(contains).strip().lower() in answer.strip().lower()
    return False


def _next_node(session: Session, form_version_id: str, from_node_id: str, answer: str) -> FormGraphNode | None:
    edges = session.execute(
        select(FormGraphEdge).where(
            FormGraphEdge.form_version_id == form_version_id,
            FormGraphEdge.from_node_id == from_node_id,
        )
    ).scalars().all()

    for edge in edges:
        if _edge_matches(edge.condition_json, answer):
            if not edge.to_node_id:
                return None
            return session.get(FormGraphNode, edge.to_node_id)
    return None


def start_session_prompt(session: Session, respondent_session: RespondentSession) -> str:
    form = session.get(Form, respondent_session.form_id)
    if not respondent_session.current_node_id:
        return "This form is complete."
    node = session.get(FormGraphNode, respondent_session.current_node_id)
    if not node:
        return "This form is not configured correctly."
    return _personalize(node.prompt, form.persona if form else "")


def process_user_message(db: Session, respondent_session: RespondentSession, user_text: str) -> FlowResult:
    if respondent_session.status != "active":
        return FlowResult(
            accepted=False,
            state=respondent_session.status,
            assistant_message="This session is no longer active.",
            current_node_key=None,
        )

    current_node = db.get(FormGraphNode, respondent_session.current_node_id)
    if not current_node:
        return FlowResult(
            accepted=False,
            state="error",
            assistant_message="Session state is invalid.",
            current_node_key=None,
        )

    db.add(Message(session_id=respondent_session.id, role="user", content=user_text))

    is_valid, reason = _validate_answer(current_node, user_text)
    if not is_valid:
        db.add(Message(session_id=respondent_session.id, role="assistant", content=reason or "Please try again."))
        db.flush()
        return FlowResult(
            accepted=False,
            state="active",
            assistant_message=reason or "Please try again.",
            current_node_key=current_node.key,
        )

    db.add(
        Answer(
            session_id=respondent_session.id,
            form_id=respondent_session.form_id,
            field_key=current_node.key,
            value_text=user_text.strip(),
        )
    )

    next_node = _next_node(db, respondent_session.form_version_id, current_node.id, user_text)
    if not next_node:
        respondent_session.status = "completed"
        respondent_session.current_node_id = None
        submission = db.execute(
            select(Submission).where(Submission.session_id == respondent_session.id)
        ).scalar_one_or_none()
        if not submission:
            db.add(Submission(form_id=respondent_session.form_id, session_id=respondent_session.id, status="completed"))
        completion_text = "Thank you. Your submission is complete."
        db.add(Message(session_id=respondent_session.id, role="assistant", content=completion_text))
        db.flush()
        return FlowResult(
            accepted=True,
            state="completed",
            assistant_message=completion_text,
            current_node_key=None,
        )

    respondent_session.current_node_id = next_node.id
    form = db.get(Form, respondent_session.form_id)
    assistant_message = _personalize(next_node.prompt, form.persona if form else "")
    db.add(Message(session_id=respondent_session.id, role="assistant", content=assistant_message))
    db.flush()

    return FlowResult(
        accepted=True,
        state="active",
        assistant_message=assistant_message,
        current_node_key=next_node.key,
    )
