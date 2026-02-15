"""DB bootstrap and seed routines for Agentic Forms v1.

Uses Alembic for migrations when available, falls back to create_all.
"""

from __future__ import annotations

import os
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import engine, SessionLocal
from .models import Base, Organization, AdminUser, Membership
from .security import hash_password

import logging

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Initialize database schema and seed defaults.

    Tries Alembic migrations first; if the migration env is not set up
    (e.g. on Vercel) it falls back to create_all.
    """
    try:
        _run_alembic_migrations()
    except Exception as exc:
        logger.warning("Alembic migration failed (%s), falling back to create_all", exc)
        Base.metadata.create_all(bind=engine)

    _seed_defaults()


def _run_alembic_migrations() -> None:
    """Run pending Alembic migrations (upgrade head)."""
    from alembic.config import Config
    from alembic import command
    import pathlib

    backend_dir = pathlib.Path(__file__).resolve().parent.parent
    alembic_cfg = Config(str(backend_dir / "alembic.ini"))

    # Override sqlalchemy.url with runtime DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    command.upgrade(alembic_cfg, "head")
    logger.info("Alembic migrations applied (upgrade head)")


def _seed_defaults() -> None:
    default_org_name = os.getenv("AGENTIC_DEFAULT_ORG_NAME", "Default Workspace")
    default_admin_email = os.getenv("AGENTIC_ADMIN_EMAIL", "admin@example.com")
    default_admin_password = os.getenv("AGENTIC_ADMIN_PASSWORD", "admin123")

    session: Session = SessionLocal()
    try:
        org = session.execute(
            select(Organization).where(Organization.name == default_org_name)
        ).scalar_one_or_none()
        if not org:
            org = Organization(name=default_org_name)
            session.add(org)
            session.flush()

        admin = session.execute(
            select(AdminUser).where(AdminUser.email == default_admin_email)
        ).scalar_one_or_none()
        if not admin:
            admin = AdminUser(
                email=default_admin_email,
                password_hash=hash_password(default_admin_password),
                full_name="Default Admin",
                is_active=True,
            )
            session.add(admin)
            session.flush()

        membership = session.execute(
            select(Membership).where(
                Membership.org_id == org.id,
                Membership.admin_user_id == admin.id,
            )
        ).scalar_one_or_none()
        if not membership:
            membership = Membership(org_id=org.id, admin_user_id=admin.id, role="org_admin")
            session.add(membership)

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
