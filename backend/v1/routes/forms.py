"""Admin form management and submissions routes."""

from __future__ import annotations

import hmac
import hashlib
import json
import uuid
from datetime import date, datetime, timedelta

import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import Date, cast, extract, func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_admin, require_org_membership
from ..models import (
    AdminUser,
    Answer,
    ApiKey,
    AuditLog,
    Form,
    FormWebhook,
    Invitation,
    Membership,
    Organization,
    RespondentSession,
    Submission,
    WebhookDelivery,
)
from ..schemas import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyResponse,
    BillingResponse,
    DashboardDailyPoint,
    DashboardFormAggregate,
    DashboardRecentSubmission,
    DropoffFunnelResponse,
    DropoffStep,
    FormAnalyticsResponse,
    FormCreateRequest,
    FormCreateResponse,
    FormDetailResponse,
    FormField,
    FormGenerateRequest,
    FormGenerateResponse,
    FormSummary,
    FormTemplateResponse,
    FormsListResponse,
    FormUpdateRequest,
    InvitationResponse,
    InviteRequest,
    OrgDashboardResponse,
    PlanInfo,
    PublishResponse,
    SubmissionRow,
    SubmissionsResponse,
    UsageSummary,
    WebhookCreateRequest,
    WebhookDeliveryResponse,
    WebhookResponse,
    FormFieldDistributionsResponse,
    FormAIInsightsResponse,
)
from ..security import generate_api_key, generate_invite_token
from ..services.export_service import export_form_submissions_to_csv
from ..services.form_generator import generate_form_from_prompt
from ..services.insights_service import compute_field_distributions, generate_ai_insights

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
        branding=f.branding or {},
        locale=f.locale or "en",
        welcome_message=f.welcome_message or "",
        completion_message=f.completion_message or "Thank you for your response!",
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
    if payload.slug is not None and payload.slug != form.slug:
        existing = db.execute(select(Form).where(Form.slug == payload.slug)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=409, detail="Slug already exists")
        form.slug = payload.slug
    if payload.persona is not None:
        form.persona = payload.persona
    if payload.mode is not None:
        form.mode = payload.mode
    if payload.system_prompt is not None:
        form.system_prompt = payload.system_prompt
    if payload.fields is not None:
        form.fields_schema = [f.model_dump() for f in payload.fields]
    if payload.branding is not None:
        form.branding = payload.branding.model_dump()
    if payload.locale is not None:
        form.locale = payload.locale
    if payload.welcome_message is not None:
        form.welcome_message = payload.welcome_message
    if payload.completion_message is not None:
        form.completion_message = payload.completion_message

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
        branding=payload.branding.model_dump() if payload.branding else {},
        locale=payload.locale,
        welcome_message=payload.welcome_message,
        completion_message=payload.completion_message,
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

@router.post("/forms/{form_id}/exports/csv")
def export_submissions_csv(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    form = db.get(Form, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_org_membership(form.org_id, current_user, db)

    csv_content, row_count = export_form_submissions_to_csv(db, form_id)
    db.add(
        AuditLog(
            org_id=form.org_id,
            actor_admin_user_id=current_user.id,
            action="form.export.csv",
            resource_type="form",
            resource_id=form.id,
            details_json={"row_count": row_count},
        )
    )
    db.commit()

    filename = f"form_{form_id}_submissions.csv"
    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Unpublish / Duplicate
# ---------------------------------------------------------------------------

@router.post("/forms/{form_id}/unpublish", response_model=PublishResponse)
def unpublish_form(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    form = db.get(Form, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_org_membership(form.org_id, current_user, db)

    form.status = "draft"
    db.add(
        AuditLog(
            org_id=form.org_id,
            actor_admin_user_id=current_user.id,
            action="form.unpublished",
            resource_type="form",
            resource_id=form.id,
        )
    )
    db.commit()
    return PublishResponse(form_id=form.id, status=form.status)


@router.post("/forms/{form_id}/duplicate", response_model=FormCreateResponse)
def duplicate_form(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    original = db.get(Form, form_id)
    if not original:
        raise HTTPException(status_code=404, detail="Form not found")
    require_org_membership(original.org_id, current_user, db)

    new_slug = f"{original.slug}-copy-{str(uuid.uuid4())[:6]}"
    form = Form(
        org_id=original.org_id,
        title=f"{original.title} (Copy)",
        description=original.description,
        slug=new_slug,
        mode=original.mode,
        persona=original.persona,
        system_prompt=original.system_prompt,
        fields_schema=original.fields_schema,
        branding=original.branding,
        locale=original.locale,
        welcome_message=original.welcome_message,
        completion_message=original.completion_message,
        status="draft",
    )
    db.add(form)
    db.flush()

    db.add(
        AuditLog(
            org_id=original.org_id,
            actor_admin_user_id=current_user.id,
            action="form.duplicated",
            resource_type="form",
            resource_id=form.id,
            details_json={"source_form_id": form_id},
        )
    )
    db.commit()

    return FormCreateResponse(id=form.id, org_id=original.org_id, slug=form.slug, status=form.status)


# ---------------------------------------------------------------------------
# Form Templates
# ---------------------------------------------------------------------------

FORM_TEMPLATES = [
    {
        "id": "customer-feedback",
        "title": "Customer Feedback",
        "description": "Collect customer satisfaction feedback and suggestions",
        "category": "feedback",
        "mode": "chat_voice",
        "persona": "Friendly and empathetic customer success agent",
        "system_prompt": "You are a friendly customer success agent collecting feedback. Ask about their overall experience, what they liked most, what could be improved, and their likelihood to recommend (1-10). Be warm and conversational.",
        "fields": [
            {"name": "overall_rating", "type": "number", "required": True, "description": "Overall satisfaction 1-10"},
            {"name": "liked_most", "type": "text", "required": True, "description": "What they liked most"},
            {"name": "improvement", "type": "text", "required": False, "description": "Areas for improvement"},
            {"name": "nps_score", "type": "number", "required": True, "description": "NPS score 1-10"},
            {"name": "email", "type": "email", "required": False, "description": "Contact email for follow-up"},
        ],
    },
    {
        "id": "job-application",
        "title": "Job Application",
        "description": "Screen job candidates with a conversational interview",
        "category": "hr",
        "mode": "chat_voice",
        "persona": "Professional and welcoming HR recruiter",
        "system_prompt": "You are a professional HR recruiter conducting an initial screening. Ask for their name, desired position, years of experience, key skills, availability, and salary expectations. Be encouraging and professional.",
        "fields": [
            {"name": "full_name", "type": "text", "required": True, "description": "Full name"},
            {"name": "email", "type": "email", "required": True, "description": "Email address"},
            {"name": "position", "type": "text", "required": True, "description": "Position applying for"},
            {"name": "experience_years", "type": "number", "required": True, "description": "Years of experience"},
            {"name": "key_skills", "type": "text", "required": True, "description": "Key relevant skills"},
            {"name": "availability", "type": "date", "required": True, "description": "Earliest start date"},
            {"name": "salary_expectation", "type": "text", "required": False, "description": "Salary expectations"},
        ],
    },
    {
        "id": "event-registration",
        "title": "Event Registration",
        "description": "Register attendees for events, workshops, or webinars",
        "category": "events",
        "mode": "chat",
        "persona": "Enthusiastic event coordinator",
        "system_prompt": "You are an enthusiastic event coordinator helping someone register. Collect their name, email, phone, company, dietary restrictions if applicable, and any questions. Be welcoming and excited about the event.",
        "fields": [
            {"name": "full_name", "type": "text", "required": True, "description": "Full name"},
            {"name": "email", "type": "email", "required": True, "description": "Email"},
            {"name": "phone", "type": "phone", "required": False, "description": "Phone number"},
            {"name": "company", "type": "text", "required": False, "description": "Company or organization"},
            {"name": "dietary_restrictions", "type": "text", "required": False, "description": "Dietary restrictions"},
            {"name": "questions", "type": "text", "required": False, "description": "Questions for organizers"},
        ],
    },
    {
        "id": "bug-report",
        "title": "Bug Report",
        "description": "Collect detailed bug reports from users",
        "category": "support",
        "mode": "chat",
        "persona": "Patient and technical support engineer",
        "system_prompt": "You are a patient support engineer collecting a bug report. Ask about what happened, what they expected to happen, steps to reproduce, browser/device info, and severity. Be empathetic and thorough.",
        "fields": [
            {"name": "summary", "type": "text", "required": True, "description": "Brief summary of the issue"},
            {"name": "steps_to_reproduce", "type": "text", "required": True, "description": "Steps to reproduce"},
            {"name": "expected_behavior", "type": "text", "required": True, "description": "What should have happened"},
            {"name": "actual_behavior", "type": "text", "required": True, "description": "What actually happened"},
            {"name": "severity", "type": "select", "required": True, "description": "Critical/High/Medium/Low"},
            {"name": "browser_device", "type": "text", "required": False, "description": "Browser and device"},
            {"name": "email", "type": "email", "required": False, "description": "Contact email"},
        ],
    },
    {
        "id": "nps-survey",
        "title": "NPS Survey",
        "description": "Quick Net Promoter Score survey",
        "category": "feedback",
        "mode": "chat_voice",
        "persona": "Concise and friendly",
        "system_prompt": "You are collecting NPS feedback. Ask how likely they are to recommend (0-10), why they gave that score, and one thing that would improve their experience. Keep it brief and conversational.",
        "fields": [
            {"name": "nps_score", "type": "number", "required": True, "description": "Likelihood to recommend 0-10"},
            {"name": "reason", "type": "text", "required": True, "description": "Reason for the score"},
            {"name": "improvement_suggestion", "type": "text", "required": False, "description": "One thing to improve"},
        ],
    },
    {
        "id": "contact-us",
        "title": "Contact Us",
        "description": "General contact form for inquiries",
        "category": "general",
        "mode": "chat",
        "persona": "Helpful and welcoming receptionist",
        "system_prompt": "You are a friendly receptionist collecting contact information. Ask for their name, email, the topic of their inquiry, and their message. Be warm and assure them someone will get back to them.",
        "fields": [
            {"name": "full_name", "type": "text", "required": True, "description": "Full name"},
            {"name": "email", "type": "email", "required": True, "description": "Email address"},
            {"name": "subject", "type": "text", "required": True, "description": "Subject or topic"},
            {"name": "message", "type": "text", "required": True, "description": "Message or inquiry"},
        ],
    },
    {
        "id": "product-feedback",
        "title": "Product Feedback",
        "description": "Gather feature requests and product feedback",
        "category": "feedback",
        "mode": "chat_voice",
        "persona": "Curious and appreciative product manager",
        "system_prompt": "You are a product manager gathering feedback. Ask which feature they use most, what's missing, their biggest pain point, and feature suggestions. Show genuine curiosity and gratitude for their input.",
        "fields": [
            {"name": "favorite_feature", "type": "text", "required": True, "description": "Most used feature"},
            {"name": "pain_point", "type": "text", "required": True, "description": "Biggest pain point"},
            {"name": "feature_request", "type": "text", "required": True, "description": "Feature they'd like to see"},
            {"name": "satisfaction_score", "type": "number", "required": True, "description": "Overall satisfaction 1-10"},
        ],
    },
    {
        "id": "lead-qualification",
        "title": "Lead Qualification",
        "description": "Qualify inbound sales leads through conversation",
        "category": "sales",
        "mode": "chat_voice",
        "persona": "Consultative and friendly sales development rep",
        "system_prompt": "You are a sales development rep qualifying a lead. Ask about their company, role, current solution, biggest challenge, timeline, and budget range. Be consultative and helpful, not pushy.",
        "fields": [
            {"name": "full_name", "type": "text", "required": True, "description": "Full name"},
            {"name": "email", "type": "email", "required": True, "description": "Work email"},
            {"name": "company", "type": "text", "required": True, "description": "Company name"},
            {"name": "role", "type": "text", "required": True, "description": "Job title"},
            {"name": "current_solution", "type": "text", "required": False, "description": "Current solution they use"},
            {"name": "challenge", "type": "text", "required": True, "description": "Main challenge to solve"},
            {"name": "timeline", "type": "text", "required": True, "description": "Decision timeline"},
            {"name": "budget_range", "type": "text", "required": False, "description": "Budget range"},
        ],
    },
    {
        "id": "employee-onboarding",
        "title": "Employee Onboarding",
        "description": "Collect new employee information during onboarding",
        "category": "hr",
        "mode": "chat",
        "persona": "Warm and organized HR coordinator",
        "system_prompt": "You are an HR coordinator helping a new employee through onboarding paperwork. Collect their full legal name, emergency contact, preferred name, start date, shirt size, and dietary preferences. Be welcoming and congratulatory.",
        "fields": [
            {"name": "legal_name", "type": "text", "required": True, "description": "Full legal name"},
            {"name": "preferred_name", "type": "text", "required": False, "description": "Preferred name"},
            {"name": "email", "type": "email", "required": True, "description": "Personal email"},
            {"name": "phone", "type": "phone", "required": True, "description": "Phone number"},
            {"name": "emergency_contact", "type": "text", "required": True, "description": "Emergency contact name and phone"},
            {"name": "start_date", "type": "date", "required": True, "description": "Start date"},
            {"name": "shirt_size", "type": "select", "required": False, "description": "T-shirt size (S/M/L/XL)"},
        ],
    },
    {
        "id": "course-evaluation",
        "title": "Course Evaluation",
        "description": "Evaluate courses, trainings, or workshops",
        "category": "education",
        "mode": "chat_voice",
        "persona": "Thoughtful academic administrator",
        "system_prompt": "You are collecting course feedback. Ask about the instructor quality (1-5), course content relevance, pace, key takeaways, and suggestions for improvement. Be open to honest feedback.",
        "fields": [
            {"name": "instructor_rating", "type": "number", "required": True, "description": "Instructor rating 1-5"},
            {"name": "content_relevance", "type": "number", "required": True, "description": "Content relevance 1-5"},
            {"name": "pace_rating", "type": "number", "required": True, "description": "Course pace 1-5"},
            {"name": "key_takeaway", "type": "text", "required": True, "description": "Key takeaway"},
            {"name": "suggestion", "type": "text", "required": False, "description": "Improvement suggestion"},
        ],
    },
    {
        "id": "patient-intake",
        "title": "Patient Intake",
        "description": "Collect patient information before appointments",
        "category": "healthcare",
        "mode": "chat",
        "persona": "Caring and professional medical receptionist",
        "system_prompt": "You are a medical receptionist collecting patient intake information. Ask for their name, date of birth, reason for visit, current medications, allergies, and insurance provider. Be caring and professional.",
        "fields": [
            {"name": "full_name", "type": "text", "required": True, "description": "Full name"},
            {"name": "date_of_birth", "type": "date", "required": True, "description": "Date of birth"},
            {"name": "phone", "type": "phone", "required": True, "description": "Phone number"},
            {"name": "reason_for_visit", "type": "text", "required": True, "description": "Reason for visit"},
            {"name": "current_medications", "type": "text", "required": False, "description": "Current medications"},
            {"name": "allergies", "type": "text", "required": False, "description": "Known allergies"},
            {"name": "insurance_provider", "type": "text", "required": False, "description": "Insurance provider"},
        ],
    },
    {
        "id": "restaurant-feedback",
        "title": "Restaurant Feedback",
        "description": "Collect dining experience feedback",
        "category": "feedback",
        "mode": "chat_voice",
        "persona": "Friendly restaurant manager",
        "system_prompt": "You are a restaurant manager collecting feedback. Ask about food quality, service, ambiance, value for money (each 1-5), and any specific comments. Be warm and genuinely interested in their experience.",
        "fields": [
            {"name": "food_quality", "type": "number", "required": True, "description": "Food quality 1-5"},
            {"name": "service_rating", "type": "number", "required": True, "description": "Service quality 1-5"},
            {"name": "ambiance", "type": "number", "required": True, "description": "Ambiance 1-5"},
            {"name": "value_for_money", "type": "number", "required": True, "description": "Value for money 1-5"},
            {"name": "comments", "type": "text", "required": False, "description": "Additional comments"},
            {"name": "would_return", "type": "boolean", "required": True, "description": "Would visit again"},
        ],
    },
    {
        "id": "newsletter-signup",
        "title": "Newsletter Signup",
        "description": "Collect email subscribers with preferences",
        "category": "marketing",
        "mode": "chat",
        "persona": "Enthusiastic content marketer",
        "system_prompt": "You are signing someone up for a newsletter. Ask for their name, email, and what topics interest them most. Be brief and enthusiastic. Let them know they can unsubscribe anytime.",
        "fields": [
            {"name": "full_name", "type": "text", "required": True, "description": "Name"},
            {"name": "email", "type": "email", "required": True, "description": "Email address"},
            {"name": "interests", "type": "text", "required": False, "description": "Topics of interest"},
        ],
    },
    {
        "id": "exit-interview",
        "title": "Exit Interview",
        "description": "Conduct employee exit interviews",
        "category": "hr",
        "mode": "chat_voice",
        "persona": "Empathetic and neutral HR professional",
        "system_prompt": "You are conducting a confidential exit interview. Ask about their reason for leaving, what they enjoyed, what could be improved, management feedback, and whether they'd consider returning. Be empathetic and assure confidentiality.",
        "fields": [
            {"name": "reason_for_leaving", "type": "text", "required": True, "description": "Primary reason for leaving"},
            {"name": "what_enjoyed", "type": "text", "required": True, "description": "What they enjoyed most"},
            {"name": "improvement_areas", "type": "text", "required": True, "description": "Areas for company improvement"},
            {"name": "management_rating", "type": "number", "required": True, "description": "Management satisfaction 1-5"},
            {"name": "would_return", "type": "boolean", "required": True, "description": "Would consider returning"},
            {"name": "additional_comments", "type": "text", "required": False, "description": "Additional comments"},
        ],
    },
    {
        "id": "market-research",
        "title": "Market Research Survey",
        "description": "Gather market insights and consumer preferences",
        "category": "research",
        "mode": "chat_voice",
        "persona": "Curious and professional market researcher",
        "system_prompt": "You are a market researcher gathering consumer insights. Ask about their awareness of the product category, current preferences, purchase frequency, decision factors, and willingness to try new options. Be genuinely curious and conversational.",
        "fields": [
            {"name": "age_group", "type": "select", "required": True, "description": "Age group (18-24, 25-34, 35-44, 45-54, 55+)"},
            {"name": "awareness", "type": "text", "required": True, "description": "Product category awareness"},
            {"name": "current_brand", "type": "text", "required": True, "description": "Current brand preference"},
            {"name": "purchase_frequency", "type": "text", "required": True, "description": "Purchase frequency"},
            {"name": "decision_factors", "type": "text", "required": True, "description": "Key purchase decision factors"},
            {"name": "openness_to_switch", "type": "number", "required": True, "description": "Willingness to try new brand 1-10"},
        ],
    },
]


@router.get("/templates", response_model=list[FormTemplateResponse])
def list_templates():
    return [
        FormTemplateResponse(
            id=t["id"],
            title=t["title"],
            description=t["description"],
            category=t["category"],
            fields=[FormField(**f) for f in t["fields"]],
            system_prompt=t["system_prompt"],
            persona=t["persona"],
            mode=t["mode"],
        )
        for t in FORM_TEMPLATES
    ]


@router.get("/templates/{template_id}", response_model=FormTemplateResponse)
def get_template(template_id: str):
    for t in FORM_TEMPLATES:
        if t["id"] == template_id:
            return FormTemplateResponse(
                id=t["id"],
                title=t["title"],
                description=t["description"],
                category=t["category"],
                fields=[FormField(**f) for f in t["fields"]],
                system_prompt=t["system_prompt"],
                persona=t["persona"],
                mode=t["mode"],
            )
    raise HTTPException(status_code=404, detail="Template not found")


# ---------------------------------------------------------------------------
# Form Analytics (advanced)
# ---------------------------------------------------------------------------

@router.get("/forms/{form_id}/analytics", response_model=FormAnalyticsResponse)
def form_analytics(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    form = db.get(Form, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_org_membership(form.org_id, current_user, db)

    total_sessions = int(
        db.scalar(
            select(func.count()).select_from(RespondentSession)
            .where(RespondentSession.form_id == form_id)
        ) or 0
    )
    total_submissions = int(
        db.scalar(
            select(func.count()).select_from(Submission)
            .where(Submission.form_id == form_id)
        ) or 0
    )
    completion_rate = round(100 * total_submissions / total_sessions, 1) if total_sessions else 0

    avg_raw = db.scalar(
        select(
            func.avg(
                extract("epoch", Submission.completed_at)
                - extract("epoch", RespondentSession.created_at)
            )
        )
        .select_from(Submission)
        .join(RespondentSession, RespondentSession.id == Submission.session_id)
        .where(Submission.form_id == form_id)
    )

    channel_rows = db.execute(
        select(RespondentSession.channel, func.count())
        .select_from(Submission)
        .join(RespondentSession, RespondentSession.id == Submission.session_id)
        .where(Submission.form_id == form_id)
        .group_by(RespondentSession.channel)
    ).all()
    channel_breakdown = {str(ch): int(cnt) for ch, cnt in channel_rows}

    # Drop-off funnel
    fields = form.fields_schema or []
    funnel: list[DropoffStep] = []
    for f_def in fields:
        key = f_def.get("name", "")
        sessions_answered = int(
            db.scalar(
                select(func.count(func.distinct(Answer.session_id)))
                .where(Answer.form_id == form_id, Answer.field_key == key)
            ) or 0
        )
        funnel.append(DropoffStep(
            field_key=key,
            field_name=f_def.get("description", key),
            sessions_reached=total_sessions,
            sessions_answered=sessions_answered,
            dropoff_pct=round(100 * (1 - sessions_answered / total_sessions), 1) if total_sessions else 0,
        ))

    return FormAnalyticsResponse(
        form_id=form_id,
        total_sessions=total_sessions,
        total_submissions=total_submissions,
        completion_rate_pct=completion_rate,
        avg_completion_seconds=float(avg_raw) if avg_raw else None,
        channel_breakdown=channel_breakdown,
        dropoff_funnel=funnel,
        sentiment_score=None,
    )


# ---------------------------------------------------------------------------
# Insights — field distributions (pure DB) and AI analysis (on-demand)
# ---------------------------------------------------------------------------

@router.get("/forms/{form_id}/insights/distributions", response_model=FormFieldDistributionsResponse)
def form_field_distributions(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    form = db.get(Form, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_org_membership(form.org_id, current_user, db)
    return compute_field_distributions(db, form)


@router.post("/forms/{form_id}/insights/generate", response_model=FormAIInsightsResponse)
def form_ai_insights(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    form = db.get(Form, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_org_membership(form.org_id, current_user, db)
    return generate_ai_insights(db, form)


# ---------------------------------------------------------------------------
# Webhooks
# ---------------------------------------------------------------------------

@router.get("/forms/{form_id}/webhooks", response_model=list[WebhookResponse])
def list_webhooks(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    form = db.get(Form, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_org_membership(form.org_id, current_user, db)

    hooks = db.execute(
        select(FormWebhook).where(FormWebhook.form_id == form_id)
    ).scalars().all()

    return [
        WebhookResponse(
            id=h.id, url=h.url, events=h.events,
            is_active=h.is_active, created_at=h.created_at.isoformat(),
        )
        for h in hooks
    ]


@router.post("/forms/{form_id}/webhooks", response_model=WebhookResponse, status_code=201)
def create_webhook(
    form_id: str,
    payload: WebhookCreateRequest,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    form = db.get(Form, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_org_membership(form.org_id, current_user, db)

    import secrets
    hook = FormWebhook(
        form_id=form_id,
        url=payload.url,
        events=payload.events,
        secret=secrets.token_hex(32),
    )
    db.add(hook)
    db.commit()
    db.refresh(hook)

    return WebhookResponse(
        id=hook.id, url=hook.url, events=hook.events,
        is_active=hook.is_active, created_at=hook.created_at.isoformat(),
    )


@router.delete("/webhooks/{webhook_id}", status_code=204)
def delete_webhook(
    webhook_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    hook = db.get(FormWebhook, webhook_id)
    if not hook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    form = db.get(Form, hook.form_id)
    if form:
        require_org_membership(form.org_id, current_user, db)
    db.delete(hook)
    db.commit()


# ---------------------------------------------------------------------------
# Team Management
# ---------------------------------------------------------------------------

@router.get("/orgs/{org_id}/members", response_model=list[dict])
def list_members(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    require_org_membership(org_id, current_user, db)
    memberships = db.execute(
        select(Membership, AdminUser)
        .join(AdminUser, AdminUser.id == Membership.admin_user_id)
        .where(Membership.org_id == org_id)
    ).all()

    return [
        {
            "id": m.id,
            "user_id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": m.role,
        }
        for m, u in memberships
    ]


@router.post("/orgs/{org_id}/invitations", response_model=InvitationResponse, status_code=201)
def invite_member(
    org_id: str,
    payload: InviteRequest,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    membership = require_org_membership(org_id, current_user, db)
    if membership.role != "org_admin":
        raise HTTPException(status_code=403, detail="Only admins can invite members")

    token = generate_invite_token()
    invitation = Invitation(
        org_id=org_id,
        email=payload.email,
        role=payload.role,
        invited_by=current_user.id,
        token=token,
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    return InvitationResponse(
        id=invitation.id,
        email=invitation.email,
        role=invitation.role,
        status=invitation.status,
    )


@router.get("/orgs/{org_id}/invitations", response_model=list[InvitationResponse])
def list_invitations(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    require_org_membership(org_id, current_user, db)
    invitations = db.execute(
        select(Invitation).where(Invitation.org_id == org_id).order_by(Invitation.created_at.desc())
    ).scalars().all()

    return [
        InvitationResponse(id=i.id, email=i.email, role=i.role, status=i.status)
        for i in invitations
    ]


@router.patch("/orgs/{org_id}/members/{membership_id}")
def update_member_role(
    org_id: str,
    membership_id: str,
    role: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    admin_membership = require_org_membership(org_id, current_user, db)
    if admin_membership.role != "org_admin":
        raise HTTPException(status_code=403, detail="Only admins can update roles")

    target = db.get(Membership, membership_id)
    if not target or target.org_id != org_id:
        raise HTTPException(status_code=404, detail="Membership not found")

    target.role = role
    db.commit()
    return {"status": "updated", "role": role}


@router.delete("/orgs/{org_id}/members/{membership_id}", status_code=204)
def remove_member(
    org_id: str,
    membership_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    admin_membership = require_org_membership(org_id, current_user, db)
    if admin_membership.role != "org_admin":
        raise HTTPException(status_code=403, detail="Only admins can remove members")

    target = db.get(Membership, membership_id)
    if not target or target.org_id != org_id:
        raise HTTPException(status_code=404, detail="Membership not found")
    if target.admin_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself")

    db.delete(target)
    db.commit()


# ---------------------------------------------------------------------------
# Billing & Usage
# ---------------------------------------------------------------------------

PLAN_LIMITS = {
    "free": {"responses": 50, "forms": 3, "voice_minutes": 0, "seats": 1},
    "pro": {"responses": 1000, "forms": 999999, "voice_minutes": 100, "seats": 3},
    "business": {"responses": 5000, "forms": 999999, "voice_minutes": 500, "seats": 10},
    "enterprise": {"responses": 999999, "forms": 999999, "voice_minutes": 999999, "seats": 999999},
}


@router.get("/orgs/{org_id}/billing", response_model=BillingResponse)
def get_billing(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    require_org_membership(org_id, current_user, db)
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    limits = PLAN_LIMITS.get(org.plan, PLAN_LIMITS["free"])

    now = datetime.utcnow()
    period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    form_ids = [f.id for f in db.execute(select(Form).where(Form.org_id == org_id)).scalars().all()]
    responses_used = int(
        db.scalar(
            select(func.count()).select_from(Submission)
            .where(
                Submission.form_id.in_(form_ids),
                Submission.completed_at >= period_start,
            )
        ) or 0
    ) if form_ids else 0

    forms_used = len(form_ids)
    seats_used = int(
        db.scalar(
            select(func.count()).select_from(Membership).where(Membership.org_id == org_id)
        ) or 0
    )

    return BillingResponse(
        plan=PlanInfo(
            plan=org.plan,
            responses_limit=limits["responses"],
            forms_limit=limits["forms"],
            voice_minutes_limit=limits["voice_minutes"],
            seats_limit=limits["seats"],
        ),
        usage=UsageSummary(
            responses_used=responses_used,
            responses_limit=limits["responses"],
            voice_minutes_used=0.0,
            voice_minutes_limit=limits["voice_minutes"],
            forms_used=forms_used,
            forms_limit=limits["forms"],
            seats_used=seats_used,
            seats_limit=limits["seats"],
            plan=org.plan,
        ),
        stripe_customer_id=org.stripe_customer_id,
    )


# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------

@router.get("/orgs/{org_id}/api-keys", response_model=list[ApiKeyResponse])
def list_api_keys(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    require_org_membership(org_id, current_user, db)
    keys = db.execute(
        select(ApiKey).where(ApiKey.org_id == org_id).order_by(ApiKey.created_at.desc())
    ).scalars().all()

    return [
        ApiKeyResponse(
            id=k.id, name=k.name, prefix=k.prefix,
            is_active=k.is_active,
            last_used_at=k.last_used_at.isoformat() if k.last_used_at else None,
            created_at=k.created_at.isoformat(),
        )
        for k in keys
    ]


@router.post("/orgs/{org_id}/api-keys", response_model=ApiKeyCreateResponse, status_code=201)
def create_api_key_route(
    org_id: str,
    payload: ApiKeyCreateRequest,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    membership = require_org_membership(org_id, current_user, db)
    if membership.role != "org_admin":
        raise HTTPException(status_code=403, detail="Only admins can create API keys")

    raw_key, key_hash, prefix = generate_api_key()
    api_key = ApiKey(
        org_id=org_id,
        name=payload.name,
        key_hash=key_hash,
        prefix=prefix,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return ApiKeyCreateResponse(id=api_key.id, name=api_key.name, prefix=prefix, key=raw_key)


@router.delete("/api-keys/{key_id}", status_code=204)
def delete_api_key(
    key_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    key = db.get(ApiKey, key_id)
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    require_org_membership(key.org_id, current_user, db)
    db.delete(key)
    db.commit()


# ---------------------------------------------------------------------------
# GDPR / Compliance
# ---------------------------------------------------------------------------

@router.post("/forms/{form_id}/retention")
def set_retention_policy(
    form_id: str,
    retention_days: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    form = db.get(Form, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    require_org_membership(form.org_id, current_user, db)

    from ..services.compliance_service import enforce_data_retention
    deleted = enforce_data_retention(db, form_id, retention_days)
    return {"deleted_sessions": deleted, "retention_days": retention_days}


@router.get("/sessions/{session_id}/export-data")
def export_session_data(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    """DSAR export: download all data for a specific respondent session."""
    from ..services.compliance_service import export_respondent_data

    session = db.get(RespondentSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    form = db.get(Form, session.form_id)
    if form:
        require_org_membership(form.org_id, current_user, db)

    return export_respondent_data(db, session_id)


@router.delete("/sessions/{session_id}/data", status_code=200)
def delete_session_data(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    """Right to erasure: delete all data for a respondent session."""
    from ..services.compliance_service import delete_respondent_data

    session = db.get(RespondentSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    form = db.get(Form, session.form_id)
    if form:
        require_org_membership(form.org_id, current_user, db)

    return delete_respondent_data(db, session_id)


# ---------------------------------------------------------------------------
# Developer API (public API via API key authentication)
# ---------------------------------------------------------------------------

from ..security import hash_api_key

@router.get("/api/v1/forms")
def api_list_forms(
    api_key: str,
    db: Session = Depends(get_db),
):
    """Public API: List forms for the org associated with the API key."""
    key_hash = hash_api_key(api_key)
    key_record = db.execute(
        select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.is_active == True)
    ).scalar_one_or_none()

    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")

    key_record.last_used_at = datetime.utcnow()

    forms = db.execute(
        select(Form).where(Form.org_id == key_record.org_id).order_by(Form.created_at.desc())
    ).scalars().all()
    db.commit()

    return {"forms": [_form_to_summary(f).model_dump() for f in forms]}


@router.get("/api/v1/forms/{form_id}/submissions")
def api_list_submissions(
    form_id: str,
    api_key: str,
    db: Session = Depends(get_db),
):
    """Public API: List submissions for a form."""
    key_hash = hash_api_key(api_key)
    key_record = db.execute(
        select(ApiKey).where(ApiKey.key_hash == key_hash, ApiKey.is_active == True)
    ).scalar_one_or_none()

    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")

    form = db.get(Form, form_id)
    if not form or form.org_id != key_record.org_id:
        raise HTTPException(status_code=404, detail="Form not found")

    key_record.last_used_at = datetime.utcnow()

    submissions = db.execute(
        select(Submission).where(Submission.form_id == form_id).order_by(Submission.completed_at.desc())
    ).scalars().all()

    rows = []
    for sub in submissions:
        answers = db.execute(
            select(Answer).where(Answer.session_id == sub.session_id)
        ).scalars().all()
        rows.append({
            "submission_id": sub.id,
            "session_id": sub.session_id,
            "completed_at": sub.completed_at.isoformat(),
            "answers": {a.field_key: a.value_text for a in answers},
        })

    db.commit()
    return {"form_id": form_id, "total": len(rows), "rows": rows}


# ---------------------------------------------------------------------------
# Messages (conversation transcripts)
# ---------------------------------------------------------------------------

from ..models import Message

@router.get("/sessions/{session_id}/transcript")
def get_session_transcript(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    """Get the full conversation transcript for a session."""
    session = db.get(RespondentSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    form = db.get(Form, session.form_id)
    if form:
        require_org_membership(form.org_id, current_user, db)

    messages = db.execute(
        select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
    ).scalars().all()

    return {
        "session_id": session_id,
        "form_id": session.form_id,
        "channel": session.channel,
        "status": session.status,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ],
    }
