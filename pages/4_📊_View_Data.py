"""View Data - Export and analyze collected data."""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import get_db_session, get_all_agents, get_conversations_by_agent, get_responses_by_conversation
from export import ExcelExporter, generate_filename
from utils import show_success, show_error

# Page config
st.set_page_config(
    page_title="View Data",
    page_icon="📊",
    layout="wide",
)

# Header
st.title("📊 View Collected Data")
st.markdown("Export and analyze conversation data")

# Sidebar - Agent selector
with st.sidebar:
    st.markdown("### 🎯 Select Agent")
    
    try:
        with get_db_session() as session:
            agents = get_all_agents(session, active_only=True)
            agent_options = {agent.name: agent.id for agent in agents}
    except Exception as e:
        st.error(f"Error loading agents: {str(e)}")
        agent_options = {}
    
    if not agent_options:
        st.warning("No agents available")
        selected_agent = None
    else:
        selected_agent_name = st.selectbox(
            "Agent",
            options=list(agent_options.keys()),
        )
        selected_agent = agent_options[selected_agent_name]
    
    st.markdown("---")
    
    st.markdown("### 📅 Date Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "From",
            value=datetime.now() - timedelta(days=30),
        )
    with col2:
        end_date = st.date_input(
            "To",
            value=datetime.now(),
        )
    
    st.markdown("---")
    
    st.markdown("### 📄 Export Format")
    export_format = st.radio(
        "Format",
        ["Excel", "CSV"],
    )
    
    export_style = st.radio(
        "Style",
        ["Long Format", "Wide Format (Google Forms)"],
        help="Long: One response per row. Wide: One conversation per row."
    )

# Main content
if not selected_agent:
    st.info("Please select an agent from the sidebar to view data")
    st.stop()

# Load data
try:
    with get_db_session() as session:
        # Get agent info
        from database import get_agent
        agent = get_agent(session, selected_agent)
        agent_dict = agent.to_dict()
        
        # Get conversations
        conversations = get_conversations_by_agent(session, selected_agent)
        
        # Get all responses for this agent
        from database import get_all_responses_with_agent_info
        all_responses = get_all_responses_with_agent_info(session, selected_agent)
        
except Exception as e:
    show_error(f"Error loading data: {str(e)}")
    st.stop()

# Display agent info
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Agent", agent_dict['name'])

with col2:
    st.metric("Total Conversations", len(conversations))

with col3:
    st.metric("Total Responses", len(all_responses))

with col4:
    st.metric("Category", agent_dict.get('category', 'N/A'))

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["📋 All Responses", "💬 By Conversation", "📊 Statistics"])

# Tab 1: All Responses
with tab1:
    st.markdown("### All Collected Responses")
    
    if not all_responses:
        st.info("No responses collected yet")
    else:
        # Convert to DataFrame
        df_data = []
        for item in all_responses:
            response = item["response"]
            conversation = item["conversation"]
            
            df_data.append({
                "Conversation ID": conversation["id"],
                "Session ID": conversation["session_id"][:12] + "...",
                "Mode": conversation["mode"],
                "Question": response["question"] or "N/A",
                "Answer": response["answer"],
                "Timestamp": response["timestamp"],
            })
        
        df = pd.DataFrame(df_data)
        
        # Display dataframe
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )
        
        # Export button
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("📥 Export Data", use_container_width=True):
                try:
                    with get_db_session() as session:
                        exporter = ExcelExporter(session)
                        
                        format_type = "excel" if export_format == "Excel" else "csv"
                        wide_format = (export_style == "Wide Format (Google Forms)")
                        
                        if wide_format:
                            data_bytes = exporter.export_wide_format(selected_agent, format_type)
                        else:
                            data_bytes = exporter.export_agent_data(selected_agent, format_type)
                        
                        filename = generate_filename(agent_dict['name'], format_type)
                        
                        st.download_button(
                            label=f"💾 Download {export_format}",
                            data=data_bytes,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if export_format == "Excel" else "text/csv",
                        )
                        
                        show_success(f"Export ready! Click Download to save.")
                        
                except Exception as e:
                    show_error(f"Error exporting data: {str(e)}")

# Tab 2: By Conversation
with tab2:
    st.markdown("### Responses by Conversation")
    
    if not conversations:
        st.info("No conversations yet")
    else:
        # Select conversation
        conversation_options = {
            f"Conv {conv.id} - {conv.session_id[:12]}... ({conv.mode})": conv.id
            for conv in conversations
        }
        
        selected_conv_name = st.selectbox(
            "Select Conversation",
            options=list(conversation_options.keys()),
        )
        selected_conv_id = conversation_options[selected_conv_name]
        
        # Get responses for this conversation
        try:
            with get_db_session() as session:
                responses = get_responses_by_conversation(session, selected_conv_id)
                
                if responses:
                    st.markdown(f"**Total Responses:** {len(responses)}")
                    
                    # Display as Q&A pairs
                    for i, response in enumerate(responses, 1):
                        with st.expander(f"Response {i} - {response.timestamp.strftime('%Y-%m-%d %H:%M')}"):
                            if response.question:
                                st.markdown(f"**❓ Question:** {response.question}")
                            st.markdown(f"**💬 Answer:** {response.answer}")
                            st.caption(f"Timestamp: {response.timestamp}")
                else:
                    st.info("No responses in this conversation")
                    
        except Exception as e:
            show_error(f"Error loading conversation: {str(e)}")

# Tab 3: Statistics
with tab3:
    st.markdown("### Data Statistics")
    
    if not all_responses:
        st.info("No data to analyze yet")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Response Metrics")
            
            # Calculate metrics
            total_responses = len(all_responses)
            questions_count = sum(1 for item in all_responses if item["response"]["question"])
            
            # Average answer length
            answer_lengths = [len(item["response"]["answer"]) for item in all_responses]
            avg_length = sum(answer_lengths) / len(answer_lengths) if answer_lengths else 0
            
            st.metric("Total Responses", total_responses)
            st.metric("Questions Asked", questions_count)
            st.metric("Avg Answer Length", f"{avg_length:.0f} chars")
        
        with col2:
            st.markdown("#### Conversation Metrics")
            
            # Mode distribution
            modes = [conv.mode for conv in conversations]
            text_count = modes.count("text")
            voice_count = modes.count("voice")
            
            st.metric("Text Conversations", text_count)
            st.metric("Voice Conversations", voice_count)
            
            # Completed conversations
            completed = sum(1 for conv in conversations if conv.ended_at)
            st.metric("Completed Conversations", completed)
        
        st.markdown("---")
        
        # Timeline chart
        st.markdown("#### Response Timeline")
        
        # Prepare data for timeline
        timeline_data = []
        for item in all_responses:
            timestamp = datetime.fromisoformat(item["response"]["timestamp"])
            timeline_data.append({
                "Date": timestamp.date(),
                "Count": 1,
            })
        
        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            df_timeline = df_timeline.groupby("Date").count().reset_index()
            
            st.line_chart(df_timeline.set_index("Date"))
        
        st.markdown("---")
        
        # Most common questions
        st.markdown("#### Most Common Questions")
        
        questions = [item["response"]["question"] for item in all_responses if item["response"]["question"]]
        
        if questions:
            from collections import Counter
            question_counts = Counter(questions)
            
            for question, count in question_counts.most_common(10):
                st.markdown(f"- **{question}** ({count} times)")
        else:
            st.info("No questions tracked yet")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #999; padding: 1rem 0;">
        <p>💡 Tip: Export data regularly to analyze trends and insights</p>
    </div>
""", unsafe_allow_html=True)

