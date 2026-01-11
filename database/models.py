"""SQLAlchemy models for Voice Agent Platform."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Agent(Base):
    """Agent model - stores agent configurations."""

    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=False)

    # Model configurations
    llm_model = Column(String(100), default="llama-3.3-70b-versatile")
    stt_model = Column(String(100), default="whisper-large-v3")
    tts_voice = Column(String(50), default="tara")

    # Generation parameters
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=500)

    # Metadata
    category = Column(String(100), nullable=True, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Usage statistics
    usage_count = Column(Integer, default=0)

    # Relationships
    conversations = relationship(
        "Conversation", back_populates="agent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', category='{self.category}')>"

    def to_dict(self):
        """Convert agent to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "instructions": self.instructions,
            "llm_model": self.llm_model,
            "stt_model": self.stt_model,
            "tts_voice": self.tts_voice,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "category": self.category,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "usage_count": self.usage_count,
        }


class Conversation(Base):
    """Conversation model - tracks conversation sessions."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey("agents.id"),
                      nullable=False, index=True)
    session_id = Column(String(100), nullable=False, unique=True, index=True)

    # Mode: 'text' or 'voice'
    mode = Column(String(20), default="text", index=True)

    # Timestamps
    started_at = Column(DateTime, default=func.now(), nullable=False)
    ended_at = Column(DateTime, nullable=True)

    # Metadata (JSON field for flexible storage)
    meta_data = Column("metadata", JSON, nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="conversations")
    responses = relationship(
        "Response", back_populates="conversation", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("ix_conversations_agent_started", "agent_id", "started_at"),
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id='{self.session_id}', mode='{self.mode}')>"

    def to_dict(self):
        """Convert conversation to dictionary."""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "mode": self.mode,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "metadata": self.meta_data,
        }


class Response(Base):
    """Response model - stores collected data from conversations."""

    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey(
        "conversations.id"), nullable=False, index=True)

    # Question and answer
    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=False)

    # Timestamp
    timestamp = Column(DateTime, default=func.now(),
                       nullable=False, index=True)

    # Metadata (JSON field for flexible data types, extracted entities, etc.)
    meta_data = Column("metadata", JSON, nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="responses")

    # Indexes
    __table_args__ = (
        Index("ix_responses_conversation_timestamp",
              "conversation_id", "timestamp"),
    )

    def __repr__(self):
        return f"<Response(id={self.id}, conversation_id={self.conversation_id}, timestamp={self.timestamp})>"

    def to_dict(self):
        """Convert response to dictionary."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "question": self.question,
            "answer": self.answer,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "metadata": self.meta_data,
        }
