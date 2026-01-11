"""Agent Marketplace - Browse and select agents."""

import streamlit as st
from database import get_db_session, get_all_agents
from utils import render_agent_card, get_or_create_session_state
from agent_system import AgentBuilder

# Page config
st.set_page_config(
    page_title="Agent Marketplace",
    page_icon="🏪",
    layout="wide",
)

# Header
st.title("🏪 Agent Marketplace")
st.markdown("Browse and interact with available voice agents")

# Initialize session state
get_or_create_session_state("selected_agent_id", None)
get_or_create_session_state("chat_mode", "text")

# Sidebar filters
with st.sidebar:
    st.markdown("### 🔍 Filters")
    
    search_query = st.text_input("Search agents", placeholder="Search by name...")
    
    category_filter = st.selectbox(
        "Category",
        ["All"] + AgentBuilder.CATEGORIES,
    )
    
    sort_by = st.selectbox(
        "Sort by",
        ["Most Used", "Newest", "Name"],
    )
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
        Browse available agents and start conversations.
        
        - **Text Chat**: Type your responses
        - **Voice Chat**: Speak naturally (requires LM Studio)
    """)

# Load agents from database
try:
    with get_db_session() as session:
        agents = get_all_agents(
            session,
            active_only=True,
            category=None if category_filter == "All" else category_filter,
        )
        
        # Convert to dictionaries
        agent_list = [agent.to_dict() for agent in agents]
        
except Exception as e:
    st.error(f"Error loading agents: {str(e)}")
    agent_list = []

# Apply search filter
if search_query:
    agent_list = [
        agent for agent in agent_list
        if search_query.lower() in agent['name'].lower() or
           search_query.lower() in (agent.get('description', '') or '').lower()
    ]

# Apply sorting
if sort_by == "Most Used":
    agent_list.sort(key=lambda x: x.get('usage_count', 0), reverse=True)
elif sort_by == "Newest":
    agent_list.sort(key=lambda x: x.get('created_at', ''), reverse=True)
elif sort_by == "Name":
    agent_list.sort(key=lambda x: x['name'])

# Display agents
if not agent_list:
    st.info("No agents found. Create your first agent!")
    if st.button("✨ Create Agent"):
        st.switch_page("pages/2_✨_Create_Agent.py")
else:
    st.markdown(f"### Found {len(agent_list)} agent(s)")
    
    # Display in grid
    cols = st.columns(2)
    
    for i, agent in enumerate(agent_list):
        with cols[i % 2]:
            render_agent_card(agent, show_actions=True)

# Quick stats
st.markdown("---")
st.markdown("### 📊 Quick Stats")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Agents", len(agent_list))

with col2:
    total_usage = sum(agent.get('usage_count', 0) for agent in agent_list)
    st.metric("Total Uses", total_usage)

with col3:
    if agent_list:
        most_used = max(agent_list, key=lambda x: x.get('usage_count', 0))
        st.metric("Most Popular", most_used['name'])

