"""Database CRUD operations for Voice Agent Platform."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from .models import Agent, Conversation, Response


# ============================================================================
# Agent Operations
# ============================================================================

def create_agent(
    session: Session,
    name: str,
    description: str,
    instructions: str,
    llm_model: str = "llama-3.3-70b-versatile",
    stt_model: str = "whisper-large-v3",
    tts_voice: str = "tara",
    temperature: float = 0.7,
    max_tokens: int = 500,
    category: Optional[str] = None,
    is_active: bool = True,
) -> Agent:
    """
    Create a new agent.

    Args:
        session: Database session
        name: Agent name
        description: Agent description
        instructions: System instructions/prompt for the agent
        llm_model: LLM model to use
        stt_model: Speech-to-text model
        tts_voice: Text-to-speech voice
        temperature: Generation temperature
        max_tokens: Maximum tokens
        category: Agent category
        is_active: Whether agent is active

    Returns:
        Created Agent object
    """
    agent = Agent(
        name=name,
        description=description,
        instructions=instructions,
        llm_model=llm_model,
        stt_model=stt_model,
        tts_voice=tts_voice,
        temperature=temperature,
        max_tokens=max_tokens,
        category=category,
        is_active=is_active,
    )
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


def get_agent(session: Session, agent_id: int) -> Optional[Agent]:
    """Get an agent by ID."""
    return session.query(Agent).filter(Agent.id == agent_id).first()


def get_agent_by_name(session: Session, name: str) -> Optional[Agent]:
    """Get an agent by name."""
    return session.query(Agent).filter(Agent.name == name).first()


def get_all_agents(
    session: Session,
    active_only: bool = True,
    category: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Agent]:
    """
    Get all agents.

    Args:
        session: Database session
        active_only: Only return active agents
        category: Filter by category
        limit: Limit number of results

    Returns:
        List of Agent objects
    """
    query = session.query(Agent)

    if active_only:
        query = query.filter(Agent.is_active == True)

    if category:
        query = query.filter(Agent.category == category)

    query = query.order_by(desc(Agent.usage_count), desc(Agent.created_at))

    if limit:
        query = query.limit(limit)

    return query.all()


def update_agent(
    session: Session,
    agent_id: int,
    **kwargs,
) -> Optional[Agent]:
    """
    Update an agent.

    Args:
        session: Database session
        agent_id: Agent ID
        **kwargs: Fields to update

    Returns:
        Updated Agent object or None if not found
    """
    agent = session.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        return None

    for key, value in kwargs.items():
        if hasattr(agent, key):
            setattr(agent, key, value)

    agent.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(agent)
    return agent


def delete_agent(session: Session, agent_id: int) -> bool:
    """
    Delete an agent (soft delete by setting is_active=False).

    Args:
        session: Database session
        agent_id: Agent ID

    Returns:
        True if deleted, False if not found
    """
    agent = session.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        return False

    agent.is_active = False
    session.commit()
    return True


def increment_agent_usage(session: Session, agent_id: int):
    """Increment the usage count for an agent."""
    agent = session.query(Agent).filter(Agent.id == agent_id).first()
    if agent:
        agent.usage_count += 1
        session.commit()


# ============================================================================
# Conversation Operations
# ============================================================================

def create_conversation(
    session: Session,
    agent_id: int,
    session_id: str,
    mode: str = "text",
    metadata: Optional[Dict[str, Any]] = None,
) -> Conversation:
    """
    Create a new conversation.

    Args:
        session: Database session
        agent_id: Agent ID
        session_id: Unique session identifier
        mode: Conversation mode ('text' or 'voice')
        metadata: Additional metadata

    Returns:
        Created Conversation object
    """
    conversation = Conversation(
        agent_id=agent_id,
        session_id=session_id,
        mode=mode,
        meta_data=metadata or {},
    )
    session.add(conversation)

    # Increment agent usage count
    increment_agent_usage(session, agent_id)

    session.commit()
    session.refresh(conversation)
    return conversation


def get_conversation(session: Session, conversation_id: int) -> Optional[Conversation]:
    """Get a conversation by ID."""
    return session.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_conversation_by_session_id(session: Session, session_id: str) -> Optional[Conversation]:
    """Get a conversation by session ID."""
    return session.query(Conversation).filter(Conversation.session_id == session_id).first()


def get_conversations_by_agent(
    session: Session,
    agent_id: int,
    limit: Optional[int] = None,
) -> List[Conversation]:
    """
    Get all conversations for an agent.

    Args:
        session: Database session
        agent_id: Agent ID
        limit: Limit number of results

    Returns:
        List of Conversation objects
    """
    query = session.query(Conversation).filter(
        Conversation.agent_id == agent_id)
    query = query.order_by(desc(Conversation.started_at))

    if limit:
        query = query.limit(limit)

    return query.all()


def end_conversation(session: Session, conversation_id: int) -> Optional[Conversation]:
    """
    End a conversation by setting ended_at timestamp.

    Args:
        session: Database session
        conversation_id: Conversation ID

    Returns:
        Updated Conversation object or None if not found
    """
    conversation = session.query(Conversation).filter(
        Conversation.id == conversation_id).first()
    if not conversation:
        return None

    conversation.ended_at = datetime.utcnow()
    session.commit()
    session.refresh(conversation)
    return conversation


# ============================================================================
# Response Operations
# ============================================================================

def create_response(
    session: Session,
    conversation_id: int,
    answer: str,
    question: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Response:
    """
    Create a new response.

    Args:
        session: Database session
        conversation_id: Conversation ID
        answer: User's answer
        question: Agent's question (optional)
        metadata: Additional metadata

    Returns:
        Created Response object
    """
    response = Response(
        conversation_id=conversation_id,
        question=question,
        answer=answer,
        meta_data=metadata or {},
    )
    session.add(response)
    session.commit()
    session.refresh(response)
    return response


def get_responses_by_conversation(
    session: Session,
    conversation_id: int,
) -> List[Response]:
    """
    Get all responses for a conversation.

    Args:
        session: Database session
        conversation_id: Conversation ID

    Returns:
        List of Response objects ordered by timestamp
    """
    return (
        session.query(Response)
        .filter(Response.conversation_id == conversation_id)
        .order_by(Response.timestamp)
        .all()
    )


def get_responses_by_agent(
    session: Session,
    agent_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Response]:
    """
    Get all responses for an agent.

    Args:
        session: Database session
        agent_id: Agent ID
        start_date: Filter responses after this date
        end_date: Filter responses before this date

    Returns:
        List of Response objects
    """
    query = (
        session.query(Response)
        .join(Conversation)
        .filter(Conversation.agent_id == agent_id)
    )

    if start_date:
        query = query.filter(Response.timestamp >= start_date)

    if end_date:
        query = query.filter(Response.timestamp <= end_date)

    return query.order_by(Response.timestamp).all()


def get_all_responses_with_agent_info(session: Session, agent_id: int) -> List[Dict[str, Any]]:
    """
    Get all responses for an agent with conversation and agent info.

    Args:
        session: Database session
        agent_id: Agent ID

    Returns:
        List of dictionaries with response, conversation, and agent data
    """
    results = (
        session.query(Response, Conversation, Agent)
        .join(Conversation, Response.conversation_id == Conversation.id)
        .join(Agent, Conversation.agent_id == Agent.id)
        .filter(Agent.id == agent_id)
        .order_by(Conversation.started_at, Response.timestamp)
        .all()
    )

    data = []
    for response, conversation, agent in results:
        data.append({
            "response": response.to_dict(),
            "conversation": conversation.to_dict(),
            "agent": agent.to_dict(),
        })

    return data
