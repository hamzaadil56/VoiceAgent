"""Admin form management and submissions routes."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Date, cast, extract, func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_admin, require_org_membership
from ..models import (
    AdminUser,
    Answer,
    AuditLog,
    Form,
    RespondentSession,
    Submission,
)
from ..schemas import (
    DashboardDailyPoint,
    DashboardFormAggregate,
    DashboardRecentSubmission,
    ExportCreateResponse,
    FormCreateRequest,
    FormCreateResponse,
    FormDetailResponse,
    FormField,
    FormGenerateRequest,
    FormGenerateResponse,
    FormSummary,
    FormsListResponse,
    FormUpdateRequest,
    OrgDashboardResponse,
    PublishResponse,
    SubmissionRow,
    SubmissionsResponse,
)
from ..services.export_service import export_form_submissions_to_csv
from ..services.form_generator import generate_form_from_prompt

router = APIRouter(tags=["v1-forms"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _form_to_summary(f: Form) -> FormSummary:
    return FormSummary(
        id=f.id,
        org_id=f.org_id,
        title=f.title,
        description=f.description,
        slug=f.slug,
        mode=f.mode,
        persona=f.persona,
        status=f.status,
        system_prompt=f.system_prompt or "",
        fields_schema=f.fields_schema or [],
        published_version_id=f.published_version_id,
        created_at=f.created_at.isoformat(),
        updated_at=f.updated_at.isoformat(),
    )


# ---------------------------------------------------------------------------
# Generate form from prompt (AI-powered)
# ---------------------------------------------------------------------------

@router.post("/orgs/{org_id}/forms/generate", response_model=FormGenerateResponse)
async def generate_form(
    org_id: str,
    payload: FormGenerateRequest,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    """Use AI to generate a form definition from a natural language prompt."""
    require_org_membership(org_id, current_user, db)

    try:
        generated = await generate_form_from_prompt(payload.prompt)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Form generation failed: {exc}")

    return FormGenerateResponse(
        title=generated.title,
        description=generated.description,
        system_prompt=generated.system_prompt,
        fields=[
            FormField(
                name=f.name,
                type=f.type,
                required=f.required,
                description=f.description,
            )
            for f in generated.fields
        ],
    )


# ---------------------------------------------------------------------------
# List forms
# ---------------------------------------------------------------------------

@router.get("/orgs/{org_id}/forms", response_model=FormsListResponse)
def list_forms(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    require_org_membership(org_id, current_user, db)
    forms = db.execute(
        select(Form).where(Form.org_id == org_id).order_by(Form.created_at.desc())
    ).scalars().all()

    return FormsListResponse(forms=[_form_to_summary(f) for f in forms])


# ---------------------------------------------------------------------------
# Org dashboard (aggregated response analytics)
# ---------------------------------------------------------------------------


@router.get("/orgs/{org_id}/dashboard", response_model=OrgDashboardResponse)
def org_dashboard(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    require_org_membership(org_id, current_user, db)
    forms = db.execute(
        select(Form).where(Form.org_id == org_id).order_by(Form.updated_at.desc())
    ).scalars().all()

    published_forms = sum(1 for f in forms if f.status == "published")
    draft_forms = sum(1 for f in forms if f.status == "draft")

    form_ids = [f.id for f in forms]
    if not form_ids:
        start_day = date.today() - timedelta(days=13)
        empty_daily: list[DashboardDailyPoint] = []
        d0 = start_day
        end_day = date.today()
        while d0 <= end_day:
            empty_daily.append(DashboardDailyPoint(date=d0.isoformat(), count=0))
            d0 += timedelta(days=1)
        return OrgDashboardResponse(
            total_submissions=0,
            total_sessions=0,
            completion_rate_pct=0.0,
            published_forms=published_forms,
            draft_forms=draft_forms,
            submissions_last_7d=0,
            submissions_prev_7d=0,
            submissions_trend_pct=None,
            completion_rate_trend_pct=None,
            avg_completion_seconds=None,
            submissions_by_channel={},
            daily_submissions=empty_daily,
            forms=[],
            recent_submissions=[],
        )

    total_submissions = db.scalar(
        select(func.count()).select_from(Submission).where(Submission.form_id.in_(form_ids))
    )
    total_submissions = int(total_submissions or 0)

    total_sessions = db.scalar(
        select(func.count())
        .select_from(RespondentSession)
        .where(RespondentSession.form_id.in_(form_ids))
    )
    total_sessions = int(total_sessions or 0)

    completion_rate_pct = round(100.0 * total_submissions / total_sessions, 1) if total_sessions else 0.0

    now = datetime.utcnow()
    boundary_7d = now - timedelta(days=7)
    boundary_14d = now - timedelta(days=14)

    submissions_last_7d = int(
        db.scalar(
            select(func.count())
            .select_from(Submission)
            .where(
                Submission.form_id.in_(form_ids),
                Submission.completed_at >= boundary_7d,
            )
        )
        or 0
    )

    submissions_prev_7d = int(
        db.scalar(
            select(func.count())
            .select_from(Submission)
            .where(
                Submission.form_id.in_(form_ids),
                Submission.completed_at >= boundary_14d,
                Submission.completed_at < boundary_7d,
            )
        )
        or 0
    )

    if submissions_prev_7d > 0:
        submissions_trend_pct = round(
            100.0 * (submissions_last_7d - submissions_prev_7d) / submissions_prev_7d,
            1,
        )
    elif submissions_last_7d > 0:
        submissions_trend_pct = 100.0
    else:
        submissions_trend_pct = None

    completed_prev = int(
        db.scalar(
            select(func.count())
            .select_from(Submission)
            .join(RespondentSession, RespondentSession.id == Submission.session_id)
            .where(
                Submission.form_id.in_(form_ids),
                Submission.completed_at >= boundary_14d,
                Submission.completed_at < boundary_7d,
            )
        )
        or 0
    )
    sessions_prev = int(
        db.scalar(
            select(func.count())
            .select_from(RespondentSession)
            .where(
                RespondentSession.form_id.in_(form_ids),
                RespondentSession.created_at < boundary_7d,
                RespondentSession.created_at >= boundary_14d,
            )
        )
        or 0
    )
    rate_prev = round(100.0 * completed_prev / sessions_prev, 1) if sessions_prev else 0.0

    completed_last = int(
        db.scalar(
            select(func.count())
            .select_from(Submission)
            .join(RespondentSession, RespondentSession.id == Submission.session_id)
            .where(
                Submission.form_id.in_(form_ids),
                Submission.completed_at >= boundary_7d,
            )
        )
        or 0
    )
    sessions_last = int(
        db.scalar(
            select(func.count())
            .select_from(RespondentSession)
            .where(
                RespondentSession.form_id.in_(form_ids),
                RespondentSession.created_at >= boundary_7d,
            )
        )
        or 0
    )
    rate_last = round(100.0 * completed_last / sessions_last, 1) if sessions_last else 0.0

    if sessions_prev > 0 or sessions_last > 0:
        completion_rate_trend_pct = round(rate_last - rate_prev, 1)
    else:
        completion_rate_trend_pct = None

    avg_raw = db.scalar(
        select(
            func.avg(
                extract("epoch", Submission.completed_at)
                - extract("epoch", RespondentSession.created_at)
            )
        )
        .select_from(Submission)
        .join(RespondentSession, RespondentSession.id == Submission.session_id)
        .where(Submission.form_id.in_(form_ids))
    )
    avg_completion_seconds = float(avg_raw) if avg_raw is not None else None

    channel_rows = db.execute(
        select(RespondentSession.channel, func.count())
        .select_from(Submission)
        .join(RespondentSession, RespondentSession.id == Submission.session_id)
        .where(Submission.form_id.in_(form_ids))
        .group_by(RespondentSession.channel)
    ).all()
    submissions_by_channel = {str(ch): int(cnt) for ch, cnt in channel_rows}

    start_day = date.today() - timedelta(days=13)
    start_dt = datetime.combine(start_day, datetime.min.time())
    day_col = cast(Submission.completed_at, Date)
    daily_rows = db.execute(
        select(day_col, func.count())
        .where(
            Submission.form_id.in_(form_ids),
            Submission.completed_at >= start_dt,
        )
        .group_by(day_col)
        .order_by(day_col)
    ).all()
    daily_map: dict[str, int] = {}
    for d, cnt in daily_rows:
        key = d.isoformat() if hasattr(d, "isoformat") else str(d)
        daily_map[key] = int(cnt)

    daily_submissions: list[DashboardDailyPoint] = []
    d = start_day
    end_day = date.today()
    while d <= end_day:
        key = d.isoformat()
        daily_submissions.append(DashboardDailyPoint(date=key, count=daily_map.get(key, 0)))
        d += timedelta(days=1)

    count_rows = db.execute(
        select(Submission.form_id, func.count())
        .where(Submission.form_id.in_(form_ids))
        .group_by(Submission.form_id)
    ).all()
    sub_counts = {fid: int(c) for fid, c in count_rows}

    form_aggregates = [
        DashboardFormAggregate(
            form_id=f.id,
            title=f.title,
            slug=f.slug,
            status=f.status,
            mode=f.mode,
            submission_count=sub_counts.get(f.id, 0),
        )
        for f in forms
    ]
    form_aggregates.sort(key=lambda x: (-x.submission_count, x.title))

    recent_rows = db.execute(
        select(Submission, Form.title)
        .join(Form, Form.id == Submission.form_id)
        .where(Form.org_id == org_id)
        .order_by(Submission.completed_at.desc())
        .limit(15)
    ).all()

    recent_submissions = [
        DashboardRecentSubmission(
            submission_id=sub.id,
            form_id=sub.form_id,
            form_title=title,
            completed_at=sub.completed_at.isoformat(),
        )
        for sub, title in recent_rows
    ]

    return OrgDashboardResponse(
        total_submissions=total_submissions,
        total_sessions=total_sessions,
        completion_rate_pct=completion_rate_pct,
        published_forms=published_forms,
        draft_forms=draft_forms,
        submissions_last_7d=submissions_last_7d,
        submissions_prev_7d=submissions_prev_7d,
        submissions_trend_pct=submissions_trend_pct,
        completion_rate_trend_pct=completion_rate_trend_pct,
        avg_completion_seconds=avg_completion_seconds,
        submissions_by_channel=submissions_by_channel,
        daily_submissions=daily_submissions,
        forms=form_aggregates,
        recent_submissions=recent_submissions,
    )


# ---------------------------------------------------------------------------
# Get single form
# ---------------------------------------------------------------------------

@router.get("/forms/{form_id}", response_model=FormDetailResponse)
def get_form(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    form = db.get(Form, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_org_membership(form.org_id, current_user, db)

    return FormDetailResponse(**_form_to_summary(form).model_dump())


# ---------------------------------------------------------------------------
# Update form
# ---------------------------------------------------------------------------

@router.patch("/forms/{form_id}", response_model=FormSummary)
def update_form(
    form_id: str,
    payload: FormUpdateRequest,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    form = db.get(Form, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_org_membership(form.org_id, current_user, db)

    if form.status == "published":
        raise HTTPException(status_code=400, detail="Cannot edit a published form directly")

    if payload.title is not None:
        form.title = payload.title
    if payload.description is not None:
        form.description = payload.description
    if payload.persona is not None:
        form.persona = payload.persona
    if payload.mode is not None:
        form.mode = payload.mode
    if payload.system_prompt is not None:
        form.system_prompt = payload.system_prompt
    if payload.fields is not None:
        form.fields_schema = [f.model_dump() for f in payload.fields]

    db.commit()
    db.refresh(form)

    return _form_to_summary(form)


# ---------------------------------------------------------------------------
# Create form (agentic — prompt + fields based)
# ---------------------------------------------------------------------------

@router.post("/orgs/{org_id}/forms", response_model=FormCreateResponse)
def create_form(
    org_id: str,
    payload: FormCreateRequest,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    require_org_membership(org_id, current_user, db)

    existing = db.execute(select(Form).where(Form.slug == payload.slug)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Slug already exists")

    form = Form(
        org_id=org_id,
        title=payload.title,
        description=payload.description,
        slug=payload.slug,
        mode=payload.mode,
        persona=payload.persona,
        system_prompt=payload.system_prompt,
        fields_schema=[f.model_dump() for f in payload.fields],
        status="draft",
    )
    db.add(form)
    db.flush()

    db.add(
        AuditLog(
            org_id=org_id,
            actor_admin_user_id=current_user.id,
            action="form.created",
            resource_type="form",
            resource_id=form.id,
        )
    )
    db.commit()

    return FormCreateResponse(
        id=form.id,
        org_id=org_id,
        slug=form.slug,
        status=form.status,
    )


# ---------------------------------------------------------------------------
# Publish form
# ---------------------------------------------------------------------------

@router.post("/forms/{form_id}/publish", response_model=PublishResponse)
def publish_form(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    form = db.get(Form, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    require_org_membership(form.org_id, current_user, db)

    # Validate the form has at least a system_prompt or fields
    if not form.system_prompt and not form.fields_schema:
        raise HTTPException(status_code=400, detail="Form must have a system prompt or fields defined")

    form.status = "published"

    db.add(
        AuditLog(
            org_id=form.org_id,
            actor_admin_user_id=current_user.id,
            action="form.published",
            resource_type="form",
            resource_id=form.id,
        )
    )
    db.commit()

    return PublishResponse(form_id=form.id, status=form.status)


# ---------------------------------------------------------------------------
# Submissions
# ---------------------------------------------------------------------------

@router.get("/forms/{form_id}/submissions", response_model=SubmissionsResponse)
def list_submissions(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    form = db.get(Form, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_org_membership(form.org_id, current_user, db)

    submissions = db.execute(
        select(Submission).where(Submission.form_id == form_id).order_by(Submission.completed_at.desc())
    ).scalars().all()

    rows: list[SubmissionRow] = []
    for submission in submissions:
        answers = db.execute(
            select(Answer).where(Answer.session_id == submission.session_id)
        ).scalars().all()
        rows.append(
            SubmissionRow(
                submission_id=submission.id,
                session_id=submission.session_id,
                completed_at=submission.completed_at.isoformat(),
                answers={a.field_key: a.value_text for a in answers},
            )
        )

    return SubmissionsResponse(form_id=form_id, total=len(rows), rows=rows)


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

@router.post("/forms/{form_id}/exports/csv", response_model=ExportCreateResponse)
def export_submissions_csv(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    form = db.get(Form, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_org_membership(form.org_id, current_user, db)

    job = export_form_submissions_to_csv(db, form_id)
    db.add(
        AuditLog(
            org_id=form.org_id,
            actor_admin_user_id=current_user.id,
            action="form.export.csv",
            resource_type="form",
            resource_id=form.id,
            details_json={"export_id": job.id, "row_count": job.row_count},
        )
    )
    db.commit()
    return ExportCreateResponse(export_id=job.id, status=job.status, row_count=job.row_count, file_path=job.file_path)
