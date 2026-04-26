"""CSV export service for submissions."""

from __future__ import annotations

import csv
import io
from collections import defaultdict
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Answer, Submission


def build_csv_content(db: Session, form_id: str) -> tuple[str, int]:
    submissions = db.execute(
        select(Submission).where(Submission.form_id == form_id)
    ).scalars().all()

    submission_ids = [s.session_id for s in submissions]
    answers = []
    if submission_ids:
        answers = db.execute(
            select(Answer).where(Answer.session_id.in_(submission_ids))
        ).scalars().all()

    answers_by_session: dict[str, dict[str, str]] = defaultdict(dict)
    field_keys: set[str] = set()
    for answer in answers:
        answers_by_session[answer.session_id][answer.field_key] = answer.value_text
        field_keys.add(answer.field_key)

    columns = ["submission_id", "session_id", "completed_at", *sorted(field_keys)]

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns)
    writer.writeheader()
    for submission in submissions:
        row: dict[str, str] = {
            "submission_id": submission.id,
            "session_id": submission.session_id,
            "completed_at": submission.completed_at.isoformat(),
        }
        row.update(answers_by_session.get(submission.session_id, {}))
        writer.writerow(row)

    return buf.getvalue(), len(submissions)


# Keep old name as alias for backward compatibility with audit logging
def export_form_submissions_to_csv(db: Session, form_id: str) -> tuple[str, int]:
    return build_csv_content(db, form_id)
