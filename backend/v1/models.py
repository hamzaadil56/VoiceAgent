"""SQLAlchemy models for Agentic Forms v1."""

from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    plan: Mapped[str] = mapped_column(String(32), default="free")
    plan_responses_limit: Mapped[int] = mapped_column(Integer, default=50)
    plan_forms_limit: Mapped[int] = mapped_column(Integer, default=3)
    plan_voice_minutes_limit: Mapped[int] = mapped_column(Integer, default=0)
    plan_seats_limit: Mapped[int] = mapped_column(Integer, default=1)

    # White-label / enterprise
    custom_domain: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    whitelabel_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    whitelabel_brand_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    whitelabel_logo_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    email_sender_domain: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # SSO configuration
    sso_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    sso_provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    sso_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # License (for self-hosted)
    license_key: Mapped[str | None] = mapped_column(String(512), nullable=True)


class AdminUser(Base, TimestampMixin):
    __tablename__ = "admin_users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), default="Admin")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    oauth_provider: Mapped[str | None] = mapped_column(String(32), nullable=True)
    oauth_provider_id: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Membership(Base, TimestampMixin):
    __tablename__ = "memberships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), index=True)
    admin_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("admin_users.id"), index=True)
    role: Mapped[str] = mapped_column(String(32), default="org_admin")

    __table_args__ = (UniqueConstraint("org_id", "admin_user_id", name="uq_membership_org_user"),)


class Invitation(Base, TimestampMixin):
    __tablename__ = "invitations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="org_editor")
    invited_by: Mapped[str] = mapped_column(String(36), ForeignKey("admin_users.id"))
    status: Mapped[str] = mapped_column(String(32), default="pending")
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    admin_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("admin_users.id"), index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Form(Base, TimestampMixin):
    __tablename__ = "forms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    mode: Mapped[str] = mapped_column(String(32), default="chat")
    persona: Mapped[str] = mapped_column(Text, default="Helpful and concise")
    status: Mapped[str] = mapped_column(String(32), default="draft")
    published_version_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("form_versions.id"), nullable=True)

    # --- Agentic form fields (prompt-based creation) ---
    system_prompt: Mapped[str] = mapped_column(Text, default="")
    fields_schema: Mapped[list] = mapped_column(JSON, default=list)

    # --- Branding ---
    branding: Mapped[dict] = mapped_column(JSON, default=dict)

    # --- Settings ---
    locale: Mapped[str] = mapped_column(String(16), default="en")
    close_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    response_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    closed_message: Mapped[str] = mapped_column(Text, default="This form is no longer accepting responses.")
    welcome_message: Mapped[str] = mapped_column(Text, default="")
    completion_message: Mapped[str] = mapped_column(Text, default="Thank you for your response!")


class FormVersion(Base, TimestampMixin):
    __tablename__ = "form_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    form_id: Mapped[str] = mapped_column(String(36), ForeignKey("forms.id"), index=True)
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(32), default="draft")
    start_node_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    __table_args__ = (UniqueConstraint("form_id", "version_number", name="uq_form_version_number"),)


class FormGraphNode(Base, TimestampMixin):
    __tablename__ = "form_graph_nodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    form_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("form_versions.id"), index=True)
    key: Mapped[str] = mapped_column(String(128), index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    node_type: Mapped[str] = mapped_column(String(32), default="question")
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    validation_json: Mapped[dict] = mapped_column(JSON, default=dict)


class FormGraphEdge(Base, TimestampMixin):
    __tablename__ = "form_graph_edges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    form_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("form_versions.id"), index=True)
    from_node_id: Mapped[str] = mapped_column(String(36), ForeignKey("form_graph_nodes.id"), index=True)
    to_node_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("form_graph_nodes.id"), nullable=True)
    condition_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class RespondentSession(Base, TimestampMixin):
    __tablename__ = "respondent_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    form_id: Mapped[str] = mapped_column(String(36), ForeignKey("forms.id"), index=True)
    form_version_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("form_versions.id"), nullable=True, index=True)
    channel: Mapped[str] = mapped_column(String(32), default="chat")
    locale: Mapped[str] = mapped_column(String(16), default="en")
    status: Mapped[str] = mapped_column(String(32), default="active")
    current_node_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("respondent_sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)


class Answer(Base, TimestampMixin):
    __tablename__ = "answers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("respondent_sessions.id"), index=True)
    form_id: Mapped[str] = mapped_column(String(36), ForeignKey("forms.id"), index=True)
    field_key: Mapped[str] = mapped_column(String(128), index=True)
    value_text: Mapped[str] = mapped_column(Text, nullable=False)


class Submission(Base, TimestampMixin):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    form_id: Mapped[str] = mapped_column(String(36), ForeignKey("forms.id"), index=True)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("respondent_sessions.id"), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="completed")
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=True)
    actor_admin_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("admin_users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_id: Mapped[str] = mapped_column(String(36), nullable=False)
    details_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ExportJob(Base, TimestampMixin):
    __tablename__ = "exports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    form_id: Mapped[str] = mapped_column(String(36), ForeignKey("forms.id"), index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    row_count: Mapped[int] = mapped_column(Integer, default=0)


# ---------------------------------------------------------------------------
# Billing & usage
# ---------------------------------------------------------------------------

class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), unique=True, index=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    plan: Mapped[str] = mapped_column(String(32), default="free")
    status: Mapped[str] = mapped_column(String(32), default="active")
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class UsageRecord(Base, TimestampMixin):
    __tablename__ = "usage_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    responses_count: Mapped[int] = mapped_column(Integer, default=0)
    voice_minutes: Mapped[float] = mapped_column(Float, default=0.0)


# ---------------------------------------------------------------------------
# Webhooks & integrations
# ---------------------------------------------------------------------------

class FormWebhook(Base, TimestampMixin):
    __tablename__ = "form_webhooks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    form_id: Mapped[str] = mapped_column(String(36), ForeignKey("forms.id"), index=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    events: Mapped[list] = mapped_column(JSON, default=list)
    secret: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    webhook_id: Mapped[str] = mapped_column(String(36), ForeignKey("form_webhooks.id"), index=True)
    event: Mapped[str] = mapped_column(String(128), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ---------------------------------------------------------------------------
# File uploads
# ---------------------------------------------------------------------------

class FileUpload(Base, TimestampMixin):
    __tablename__ = "file_uploads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("respondent_sessions.id"), nullable=True, index=True)
    form_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("forms.id"), nullable=True, index=True)
    field_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    content_type: Mapped[str] = mapped_column(String(128), default="application/octet-stream")
    storage_path: Mapped[str] = mapped_column(String(2048), nullable=False)


# ---------------------------------------------------------------------------
# API Keys (developer access)
# ---------------------------------------------------------------------------

class ApiKey(Base, TimestampMixin):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    prefix: Mapped[str] = mapped_column(String(16), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
