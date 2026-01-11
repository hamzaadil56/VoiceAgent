"""Streamlit helper utilities for Voice Agent Platform."""

import streamlit as st
from typing import Any, Dict, Optional
from datetime import datetime

from database import init_db


def initialize_database():
    """Initialize the database on app startup."""
    try:
        init_db()
        return True
    except Exception as e:
        st.error(f"Failed to initialize database: {str(e)}")
        return False


def get_or_create_session_state(key: str, default: Any) -> Any:
    """
    Get or create a session state variable.

    Args:
        key: Session state key
        default: Default value if key doesn't exist

    Returns:
        Value from session state
    """
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]


def render_agent_card(agent: Dict[str, Any], show_actions: bool = True):
    """
    Render an agent card.

    Args:
        agent: Agent dictionary
        show_actions: Show action buttons
    """
    with st.container():
        st.markdown(
            f"""
            <div style="
                padding: 1.5rem;
                border-radius: 0.5rem;
                border: 1px solid #e0e0e0;
                background-color: #f8f9fa;
                margin-bottom: 1rem;
            ">
                <h3 style="margin-top: 0; color: #1f77b4;">{agent['name']}</h3>
                <p style="color: #666; margin-bottom: 0.5rem;">{agent.get('description', 'No description')}</p>
                <div style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                    <span style="
                        padding: 0.25rem 0.75rem;
                        border-radius: 1rem;
                        background-color: #e3f2fd;
                        color: #1976d2;
                        font-size: 0.875rem;
                    ">{agent.get('category', 'Other')}</span>
                    <span style="color: #999; font-size: 0.875rem;">🎤 {agent.get('tts_voice', 'tara')}</span>
                    <span style="color: #999; font-size: 0.875rem;">💬 {agent.get('usage_count', 0)} uses</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if show_actions:
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("💬 Start Text Chat", key=f"text_chat_{agent['id']}"):
                    st.session_state.selected_agent_id = agent['id']
                    st.session_state.chat_mode = "text"
                    st.switch_page("pages/3_💬_Chat_Interface.py")
            with col2:
                if st.button("🎤 Start Voice Chat", key=f"voice_chat_{agent['id']}"):
                    st.session_state.selected_agent_id = agent['id']
                    st.session_state.chat_mode = "voice"
                    st.switch_page("pages/3_💬_Chat_Interface.py")


def render_chat_message(role: str, content: str, timestamp: Optional[str] = None):
    """
    Render a chat message.

    Args:
        role: Message role ('user' or 'assistant')
        content: Message content
        timestamp: Optional timestamp
    """
    if role == "user":
        avatar = "👤"
        align = "right"
        bg_color = "#e3f2fd"
    else:
        avatar = "🤖"
        align = "left"
        bg_color = "#f5f5f5"

    with st.container():
        col1, col2, col3 = st.columns([1, 10, 1])

        if align == "left":
            with col1:
                st.markdown(
                    f"<div style='font-size: 2rem;'>{avatar}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(
                    f"""
                    <div style="
                        padding: 1rem;
                        border-radius: 0.5rem;
                        background-color: {bg_color};
                        margin-bottom: 0.5rem;
                    ">
                        <p style="margin: 0;">{content}</p>
                        {f'<p style="font-size: 0.75rem; color: #999; margin: 0.5rem 0 0 0;">{timestamp}</p>' if timestamp else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            with col2:
                st.markdown(
                    f"""
                    <div style="
                        padding: 1rem;
                        border-radius: 0.5rem;
                        background-color: {bg_color};
                        margin-bottom: 0.5rem;
                        text-align: right;
                    ">
                        <p style="margin: 0;">{content}</p>
                        {f'<p style="font-size: 0.75rem; color: #999; margin: 0.5rem 0 0 0;">{timestamp}</p>' if timestamp else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col3:
                st.markdown(
                    f"<div style='font-size: 2rem;'>{avatar}</div>", unsafe_allow_html=True)


def format_datetime(dt: datetime) -> str:
    """
    Format datetime for display.

    Args:
        dt: Datetime object

    Returns:
        Formatted string
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def show_success(message: str):
    """Show success message."""
    st.success(f"✅ {message}")


def show_error(message: str):
    """Show error message."""
    st.error(f"❌ {message}")


def show_info(message: str):
    """Show info message."""
    st.info(f"ℹ️ {message}")


def show_warning(message: str):
    """Show warning message."""
    st.warning(f"⚠️ {message}")
