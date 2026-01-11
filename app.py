"""Voice Agent Platform - Main Streamlit App."""

import streamlit as st
from utils import initialize_database, get_or_create_session_state
from database import get_db_session, get_all_agents
import os

# Page config
st.set_page_config(
    page_title="Voice Agent Platform",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.25rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }
    .stat-label {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database
if "db_initialized" not in st.session_state:
    st.session_state.db_initialized = initialize_database()

# Initialize session state
get_or_create_session_state("selected_agent_id", None)
get_or_create_session_state("chat_mode", "text")

# Header
st.markdown('<h1 class="main-header">🎙️ Voice Agent Platform</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Build, deploy, and manage AI voice agents that collect data through natural conversations</p>',
    unsafe_allow_html=True
)

# Main content
st.markdown("---")

# Features section
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        ### 🏪 Agent Marketplace
        Browse and use pre-built voice agents or create your own. 
        Each agent is designed for specific use cases like interviews, 
        surveys, or customer feedback.
    """)

with col2:
    st.markdown("""
        ### 💬 Conversational Interface
        Interact with agents through text or voice. Agents ask questions
        naturally and collect structured data that can be exported like
        Google Forms.
    """)

with col3:
    st.markdown("""
        ### 📊 Data Collection
        All conversations are automatically saved. Export collected data
        to Excel/CSV for analysis. Perfect for research, validation,
        and feedback collection.
    """)

st.markdown("---")

# Statistics
try:
    with get_db_session() as session:
        agents = get_all_agents(session, active_only=True)
        total_agents = len(agents)
        total_usage = sum(agent.usage_count for agent in agents)
        
        from database.models import Conversation, Response
        total_conversations = session.query(Conversation).count()
        total_responses = session.query(Response).count()
        
    st.markdown("### 📈 Platform Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                <p class="stat-number">{total_agents}</p>
                <p class="stat-label">Active Agents</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <p class="stat-number">{total_conversations}</p>
                <p class="stat-label">Conversations</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <p class="stat-number">{total_responses}</p>
                <p class="stat-label">Responses Collected</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="stat-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <p class="stat-number">{total_usage}</p>
                <p class="stat-label">Total Uses</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading statistics: {str(e)}")

st.markdown("---")

# Quick start
st.markdown("### 🚀 Quick Start")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 1️⃣ Browse Agents")
    st.markdown("Check out the **Agent Marketplace** to see available agents")
    if st.button("🏪 Go to Marketplace", use_container_width=True):
        st.switch_page("pages/1_🏪_Agent_Marketplace.py")

with col2:
    st.markdown("#### 2️⃣ Create Your Agent")
    st.markdown("Build a custom agent for your specific needs")
    if st.button("✨ Create Agent", use_container_width=True):
        st.switch_page("pages/2_✨_Create_Agent.py")

with col3:
    st.markdown("#### 3️⃣ View Data")
    st.markdown("Export and analyze collected conversation data")
    if st.button("📊 View Data", use_container_width=True):
        st.switch_page("pages/4_📊_View_Data.py")

st.markdown("---")

# Use cases
st.markdown("### 💡 Use Cases")

use_cases = [
    {
        "title": "Startup Validation",
        "description": "Validate your startup idea through structured questions",
        "icon": "🚀"
    },
    {
        "title": "Job Interviews",
        "description": "Practice interview skills with an AI interviewer",
        "icon": "💼"
    },
    {
        "title": "Customer Feedback",
        "description": "Collect detailed customer feedback and satisfaction data",
        "icon": "⭐"
    },
    {
        "title": "Market Research",
        "description": "Conduct surveys and gather market insights",
        "icon": "📊"
    },
    {
        "title": "User Testing",
        "description": "Get user feedback on products and features",
        "icon": "🧪"
    },
    {
        "title": "Education",
        "description": "Create educational assessments and tutoring agents",
        "icon": "📚"
    },
]

cols = st.columns(3)
for i, use_case in enumerate(use_cases):
    with cols[i % 3]:
        st.markdown(f"""
            <div style="
                padding: 1rem;
                border-radius: 0.5rem;
                border: 1px solid #e0e0e0;
                margin-bottom: 1rem;
                background-color: #f8f9fa;
            ">
                <h4 style="margin: 0 0 0.5rem 0;">{use_case['icon']} {use_case['title']}</h4>
                <p style="margin: 0; color: #666; font-size: 0.9rem;">{use_case['description']}</p>
            </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Footer
st.markdown("""
    <div style="text-align: center; color: #999; padding: 2rem 0;">
        <p>Built with ❤️ using OpenAI Agents SDK, Groq, and Streamlit</p>
        <p style="font-size: 0.875rem;">
            Powered by Groq's Whisper STT • Llama LLM • Orpheus TTS
        </p>
    </div>
""", unsafe_allow_html=True)

# Sidebar info
with st.sidebar:
    st.markdown("### 📌 Navigation")
    st.markdown("""
        - 🏪 **Marketplace**: Browse available agents
        - ✨ **Create Agent**: Build your own agent
        - 💬 **Chat Interface**: Talk with agents
        - 📊 **View Data**: Export and analyze data
    """)
    
    st.markdown("---")
    
    st.markdown("### ⚙️ System Status")
    
    # Check Groq API key
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        st.success("✅ Groq API configured")
    else:
        st.error("❌ Groq API key missing")
    
    # Check Database
    if st.session_state.get("db_initialized"):
        st.success("✅ Database connected")
    else:
        st.error("❌ Database not initialized")
    
    # Check LM Studio (optional for voice)
    lm_studio_url = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
    st.info(f"🎤 Voice TTS: {lm_studio_url}")
    st.caption("LM Studio required for voice mode")

