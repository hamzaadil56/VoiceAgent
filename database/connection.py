"""Database connection management for Voice Agent Platform."""

import os
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

from .models import Base

# Load environment variables (gracefully handle permission issues)
try:
    load_dotenv()
except (PermissionError, FileNotFoundError):
    # .env file may not be accessible, use environment variables directly
    pass

# Database URL from environment or default to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL")

# If no DATABASE_URL is provided, use SQLite
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./voiceagent.db"
    print("⚠️  No DATABASE_URL found in .env, using SQLite: voiceagent.db")
else:
    print(
        f"✓ Connected to database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'SQLite'}")

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    # SQLite-specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Set to True for SQL debugging
    )

    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # PostgreSQL configuration with connection pooling
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using
        echo=False,  # Set to True for SQL debugging
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize the database by creating all tables."""
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"✗ Error creating database tables: {str(e)}")
        raise


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Get a database session with context manager.

    Usage:
        with get_db_session() as session:
            # Use session here
            pass
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_db() -> Session:
    """
    Get a database session (for non-context manager usage).
    Remember to close the session when done.

    Returns:
        Database session
    """
    return SessionLocal()
