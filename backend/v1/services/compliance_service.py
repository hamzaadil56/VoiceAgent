"""GDPR and compliance service for data management."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from ..models import (
    Answer,
    Form,
    Message,
    RespondentSession,
    Submission,
)

logger = logging.getLogger(__name__)


def export_respondent_data(db: Session, session_id: str) -> dict:
    """Export all data associated with a respondent session (DSAR compliance)."""
    session = db.get(RespondentSession, session_id)
    if not session:
        return {"error": "Session not found"}

    messages = db.execute(
        select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
    ).scalars().all()

    answers = db.execute(
        select(Answer).where(Answer.session_id == session_id)
    ).scalars().all()

    submission = db.execute(
        select(Submission).where(Submission.session_id == session_id)
    ).scalar_one_or_none()

    return {
        "session": {
            "id": session.id,
            "form_id": session.form_id,
            "channel": session.channel,
            "locale": session.locale,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
        },
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
        "answers": [
            {
                "field_key": a.field_key,
                "value": a.value_text,
                "created_at": a.created_at.isoformat(),
            }
            for a in answers
        ],
        "submission": {
            "id": submission.id,
            "status": submission.status,
            "completed_at": submission.completed_at.isoformat(),
        }
        if submission
        else None,
    }


def delete_respondent_data(db: Session, session_id: str) -> dict:
    """Delete all data associated with a respondent session (right to erasure)."""
    session = db.get(RespondentSession, session_id)
    if not session:
        return {"error": "Session not found", "deleted": False}

    db.execute(delete(Message).where(Message.session_id == session_id))
    db.execute(delete(Answer).where(Answer.session_id == session_id))
    db.execute(delete(Submission).where(Submission.session_id == session_id))
    db.delete(session)
    db.commit()

    logger.info("Deleted respondent data for session %s", session_id)
    return {"session_id": session_id, "deleted": True}


def enforce_data_retention(db: Session, form_id: str, retention_days: int) -> int:
    """Delete sessions older than retention_days for a form."""
    cutoff = datetime.utcnow() - timedelta(days=retention_days)

    old_sessions = db.execute(
        select(RespondentSession).where(
            RespondentSession.form_id == form_id,
            RespondentSession.created_at < cutoff,
        )
    ).scalars().all()

    deleted_count = 0
    for session in old_sessions:
        db.execute(delete(Message).where(Message.session_id == session.id))
        db.execute(delete(Answer).where(Answer.session_id == session.id))
        db.execute(delete(Submission).where(Submission.session_id == session.id))
        db.delete(session)
        deleted_count += 1

    if deleted_count > 0:
        db.commit()
        logger.info(
            "Retention cleanup: deleted %d sessions for form %s (cutoff: %s)",
            deleted_count, form_id, cutoff.isoformat(),
        )

    return deleted_count
