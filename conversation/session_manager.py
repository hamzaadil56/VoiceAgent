"""Session Manager - Track and manage conversation sessions."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from database import (
    create_conversation,
    get_conversation,
    get_conversation_by_session_id,
    end_conversation as db_end_conversation,
)


class SessionManager:
    """
    Manage conversation sessions.

    Handles session creation, tracking, and persistence to database.
    """

    def __init__(self, db_session: Session):
        """
        Initialize session manager.

        Args:
            db_session: Database session
        """
        self.db_session = db_session
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(
        self,
        agent_id: int,
        mode: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a new conversation session.

        Args:
            agent_id: Agent ID
            mode: Conversation mode ('text' or 'voice')
            metadata: Additional metadata

        Returns:
            Session ID
        """
        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Create conversation in database
        conversation = create_conversation(
            self.db_session,
            agent_id=agent_id,
            session_id=session_id,
            mode=mode,
            metadata=metadata,
        )

        # Store in active sessions
        self.active_sessions[session_id] = {
            "conversation_id": conversation.id,
            "agent_id": agent_id,
            "mode": mode,
            "started_at": conversation.started_at,
            "message_count": 0,
            "metadata": metadata or {},
        }

        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information.

        Args:
            session_id: Session ID

        Returns:
            Session information dictionary or None if not found
        """
        # Try to get from active sessions first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]

        # Try to get from database
        conversation = get_conversation_by_session_id(
            self.db_session, session_id)
        if conversation:
            session_info = {
                "conversation_id": conversation.id,
                "agent_id": conversation.agent_id,
                "mode": conversation.mode,
                "started_at": conversation.started_at,
                "ended_at": conversation.ended_at,
                "metadata": conversation.meta_data or {},
            }

            # Add to active sessions if not ended
            if not conversation.ended_at:
                self.active_sessions[session_id] = session_info

            return session_info

        return None

    def get_conversation_id(self, session_id: str) -> Optional[int]:
        """
        Get conversation ID from session ID.

        Args:
            session_id: Session ID

        Returns:
            Conversation ID or None if not found
        """
        session = self.get_session(session_id)
        return session["conversation_id"] if session else None

    def increment_message_count(self, session_id: str):
        """
        Increment message count for a session.

        Args:
            session_id: Session ID
        """
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["message_count"] += 1

    def update_metadata(self, session_id: str, metadata: Dict[str, Any]):
        """
        Update session metadata.

        Args:
            session_id: Session ID
            metadata: Metadata to update
        """
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["metadata"].update(metadata)

    def end_session(self, session_id: str) -> bool:
        """
        End a conversation session.

        Args:
            session_id: Session ID

        Returns:
            True if ended successfully, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False

        # End conversation in database
        conversation = db_end_conversation(
            self.db_session,
            session["conversation_id"],
        )

        # Remove from active sessions
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

        return conversation is not None

    def is_active(self, session_id: str) -> bool:
        """
        Check if a session is active.

        Args:
            session_id: Session ID

        Returns:
            True if active, False otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return False

        # Check if ended
        return session.get("ended_at") is None

    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active sessions.

        Returns:
            Dictionary of active sessions
        """
        return self.active_sessions.copy()

    def get_session_duration(self, session_id: str) -> Optional[float]:
        """
        Get session duration in seconds.

        Args:
            session_id: Session ID

        Returns:
            Duration in seconds or None if not found
        """
        session = self.get_session(session_id)
        if not session:
            return None

        started_at = session["started_at"]
        ended_at = session.get("ended_at")

        if ended_at:
            # Completed session
            duration = (ended_at - started_at).total_seconds()
        else:
            # Active session
            duration = (datetime.utcnow() - started_at).total_seconds()

        return duration

    def cleanup_inactive_sessions(self, max_duration_hours: int = 24):
        """
        Clean up inactive sessions older than max_duration_hours.

        Args:
            max_duration_hours: Maximum session duration in hours
        """
        current_time = datetime.utcnow()
        sessions_to_remove = []

        for session_id, session_info in self.active_sessions.items():
            started_at = session_info["started_at"]
            duration_hours = (current_time - started_at).total_seconds() / 3600

            if duration_hours > max_duration_hours:
                # Auto-end the session
                self.end_session(session_id)
                sessions_to_remove.append(session_id)

        # Remove from active sessions
        for session_id in sessions_to_remove:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
