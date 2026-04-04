"""CSV export service for submissions."""

from __future__ import annotations

import csv
import os
from collections import defaultdict
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Answer, ExportJob, Submission


def export_form_submissions_to_csv(db: Session, form_id: str) -> ExportJob:
    submissions = db.execute(
        select(Submission).where(Submission.form_id == form_id)
    ).scalars().all()

    submission_ids = [s.session_id for s in submissions]
    answers = []
    if submission_ids:
        answers = db.execute(
            select(Answer).where(Answer.session_id.in_(submission_ids))
        ).scalars().all()

    answers_by_session = defaultdict(dict)
    field_keys = set()
    for answer in answers:
        answers_by_session[answer.session_id][answer.field_key] = answer.value_text
        field_keys.add(answer.field_key)

    columns = ["submission_id", "session_id", "completed_at", *sorted(field_keys)]

    export_dir = os.path.join("/tmp", "agentic_exports")
    os.makedirs(export_dir, exist_ok=True)
    file_name = f"form_{form_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    file_path = os.path.join(export_dir, file_name)

    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=columns)
        writer.writeheader()
        for submission in submissions:
            row = {
                "submission_id": submission.id,
                "session_id": submission.session_id,
                "completed_at": submission.completed_at.isoformat(),
            }
            row.update(answers_by_session.get(submission.session_id, {}))
            writer.writerow(row)

    export_job = ExportJob(form_id=form_id, status="completed", row_count=len(submissions), file_path=file_path)
    db.add(export_job)
    db.flush()
    return export_job
