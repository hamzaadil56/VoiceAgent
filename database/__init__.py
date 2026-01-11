"""Database package for Voice Agent Platform."""

from .models import Agent, Conversation, Response
from .connection import get_db_session, init_db
from .operations import (
    create_agent,
    get_agent,
    get_all_agents,
    update_agent,
    delete_agent,
    create_conversation,
    get_conversation,
    get_conversation_by_session_id,
    get_conversations_by_agent,
    end_conversation,
    create_response,
    get_responses_by_conversation,
    get_responses_by_agent,
)

__all__ = [
    # Models
    "Agent",
    "Conversation",
    "Response",
    # Connection
    "get_db_session",
    "init_db",
    # Operations
    "create_agent",
    "get_agent",
    "get_all_agents",
    "update_agent",
    "delete_agent",
    "create_conversation",
    "get_conversation",
    "get_conversation_by_session_id",
    "get_conversations_by_agent",
    "end_conversation",
    "create_response",
    "get_responses_by_conversation",
    "get_responses_by_agent",
]

