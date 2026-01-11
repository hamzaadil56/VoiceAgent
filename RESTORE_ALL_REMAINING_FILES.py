#!/usr/bin/env python3
"""
Voice Agent Platform - Master Restoration Script
Creates ALL remaining implementation files in one go.

Run this script to complete the restoration:
    python3 RESTORE_ALL_REMAINING_FILES.py
"""

import os
from pathlib import Path

print("=" * 70)
print("🎙️  VOICE AGENT PLATFORM - MASTER RESTORATION")
print("=" * 70)
print()
print("This script will create all remaining implementation files.")
print("Files to create: 14")
print()

# File contents dictionary - contains all code
FILES = {

# ============================================================================
# CONVERSATION MANAGEMENT
# ============================================================================

"conversation/session_manager.py": '''"""Session Manager - Track and manage conversation sessions."""

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
        conversation = get_conversation_by_session_id(self.db_session, session_id)
        if conversation:
            session_info = {
                "conversation_id": conversation.id,
                "agent_id": conversation.agent_id,
                "mode": conversation.mode,
                "started_at": conversation.started_at,
                "ended_at": conversation.ended_at,
                "metadata": conversation.metadata or {},
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
''',

"conversation/data_collector.py": '''"""Data Collector - Extract and store conversation data."""

import re
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session

from database import create_response, get_responses_by_conversation


class DataCollector:
    """
    Collect and store data from conversations.
    
    Extracts questions and answers from conversations and stores them
    in a structured format for later analysis and export.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize data collector.
        
        Args:
            db_session: Database session
        """
        self.db_session = db_session
        
        # Patterns to detect questions
        self.question_patterns = [
            r'\\?$',  # Ends with question mark
            r'^(what|who|where|when|why|how|can|could|would|should|do|does|did|is|are|was|were)\\b',  # Question words
            r'\\btell me\\b',  # "Tell me about..."
            r'\\bdescribe\\b',  # "Describe..."
            r'\\bexplain\\b',  # "Explain..."
        ]
    
    def collect(
        self,
        conversation_id: int,
        user_message: str,
        agent_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Collect a response from the conversation.
        
        Args:
            conversation_id: Conversation ID
            user_message: User's message (answer)
            agent_message: Agent's previous message (question, optional)
            metadata: Additional metadata
            
        Returns:
            Response ID
        """
        # Detect if agent_message is a question
        question = None
        if agent_message:
            if self._is_question(agent_message):
                question = agent_message
        
        # Create response in database
        response = create_response(
            self.db_session,
            conversation_id=conversation_id,
            answer=user_message,
            question=question,
            metadata=metadata,
        )
        
        return response.id
    
    def collect_qa_pair(
        self,
        conversation_id: int,
        question: str,
        answer: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Collect a question-answer pair.
        
        Args:
            conversation_id: Conversation ID
            question: The question
            answer: The answer
            metadata: Additional metadata
            
        Returns:
            Response ID
        """
        response = create_response(
            self.db_session,
            conversation_id=conversation_id,
            answer=answer,
            question=question,
            metadata=metadata,
        )
        
        return response.id
    
    def _is_question(self, text: str) -> bool:
        """
        Detect if text is a question.
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be a question
        """
        text = text.strip().lower()
        
        for pattern in self.question_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def get_conversation_data(
        self,
        conversation_id: int,
    ) -> List[Dict[str, Any]]:
        """
        Get all collected data for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of response dictionaries
        """
        responses = get_responses_by_conversation(self.db_session, conversation_id)
        return [response.to_dict() for response in responses]
    
    def extract_structured_data(
        self,
        conversation_id: int,
    ) -> Dict[str, Any]:
        """
        Extract structured data from a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dictionary with structured data
        """
        responses = get_responses_by_conversation(self.db_session, conversation_id)
        
        structured_data = {
            "conversation_id": conversation_id,
            "total_responses": len(responses),
            "questions": [],
            "answers": [],
            "qa_pairs": [],
            "timestamps": [],
        }
        
        for response in responses:
            if response.question:
                structured_data["questions"].append(response.question)
                structured_data["qa_pairs"].append({
                    "question": response.question,
                    "answer": response.answer,
                    "timestamp": response.timestamp.isoformat(),
                })
            
            structured_data["answers"].append(response.answer)
            structured_data["timestamps"].append(response.timestamp.isoformat())
        
        return structured_data
    
    def get_summary_stats(
        self,
        conversation_id: int,
    ) -> Dict[str, Any]:
        """
        Get summary statistics for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dictionary with summary statistics
        """
        responses = get_responses_by_conversation(self.db_session, conversation_id)
        
        if not responses:
            return {
                "total_responses": 0,
                "total_questions": 0,
                "avg_answer_length": 0,
                "first_response": None,
                "last_response": None,
            }
        
        questions_count = sum(1 for r in responses if r.question)
        total_answer_length = sum(len(r.answer) for r in responses)
        avg_answer_length = total_answer_length / len(responses) if responses else 0
        
        return {
            "total_responses": len(responses),
            "total_questions": questions_count,
            "avg_answer_length": round(avg_answer_length, 2),
            "first_response": responses[0].timestamp.isoformat() if responses else None,
            "last_response": responses[-1].timestamp.isoformat() if responses else None,
        }


class ConversationTracker:
    """
    Track conversation flow and extract data in real-time.
    
    This is a helper class that can be used to track the conversation
    as it happens, maintaining state between messages.
    """
    
    def __init__(self, conversation_id: int, data_collector: DataCollector):
        """
        Initialize conversation tracker.
        
        Args:
            conversation_id: Conversation ID
            data_collector: DataCollector instance
        """
        self.conversation_id = conversation_id
        self.data_collector = data_collector
        
        # Track the last agent message (potential question)
        self.last_agent_message: Optional[str] = None
        self.message_history: List[Dict[str, str]] = []
    
    def add_user_message(self, message: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a user message and collect data.
        
        Args:
            message: User's message
            metadata: Additional metadata
        """
        # Store in history
        self.message_history.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Collect data with the last agent message as the question
        self.data_collector.collect(
            conversation_id=self.conversation_id,
            user_message=message,
            agent_message=self.last_agent_message,
            metadata=metadata,
        )
    
    def add_agent_message(self, message: str):
        """
        Add an agent message.
        
        Args:
            message: Agent's message
        """
        # Store in history
        self.message_history.append({
            "role": "assistant",
            "content": message,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Store as last agent message (potential question for next response)
        self.last_agent_message = message
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Get conversation history.
        
        Returns:
            List of message dictionaries
        """
        return self.message_history.copy()
    
    def get_collected_data(self) -> List[Dict[str, Any]]:
        """
        Get all collected data for this conversation.
        
        Returns:
            List of response dictionaries
        """
        return self.data_collector.get_conversation_data(self.conversation_id)
''',

# Continue in next part...
}

# Create all files
print("Creating files...")
print()

created_count = 0
for filepath, content in FILES.items():
    try:
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"✅ Created: {filepath}")
        created_count += 1
    except Exception as e:
        print(f"❌ Error creating {filepath}: {str(e)}")

print()
print("=" * 70)
print(f"✅ Created {created_count}/{len(FILES)} files!")
print("=" * 70)
print()
print("⚠️  NOTE: This script contains the first 2 files.")
print("   Due to size limits, remaining files need to be added.")
print()
print("SOLUTION: I'll continue adding more files to this script in parts.")
print("Stay tuned...")

