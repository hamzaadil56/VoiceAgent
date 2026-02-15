"""Shared test fixtures for backend tests."""

import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend root is on path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "src"))
sys.path.insert(0, str(backend_dir.parent))

# Use in-memory SQLite for tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret-key"
os.environ["AGENTIC_ADMIN_EMAIL"] = "test@example.com"
os.environ["AGENTIC_ADMIN_PASSWORD"] = "testpass123"


@pytest.fixture
def db_session():
    """Create a fresh in-memory database session for each test."""
    from v1.models import Base

    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
