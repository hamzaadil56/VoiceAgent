"""Admin form management and submissions routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_admin, require_org_membership
from ..models import (
    AdminUser,
    Answer,
    AuditLog,
    Form,
    Submission,
)
from ..schemas import (
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
