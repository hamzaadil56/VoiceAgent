"""SQLAlchemy models for Agentic Forms v1."""

from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
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


class AdminUser(Base, TimestampMixin):
    __tablename__ = "admin_users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), default="Admin")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Membership(Base, TimestampMixin):
    __tablename__ = "memberships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), index=True)
    admin_user_id: Mapped[str] = mapped_column(String(36), ForeignKey("admin_users.id"), index=True)
    role: Mapped[str] = mapped_column(String(32), default="org_admin")

    __table_args__ = (UniqueConstraint("org_id", "admin_user_id", name="uq_membership_org_user"),)


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
