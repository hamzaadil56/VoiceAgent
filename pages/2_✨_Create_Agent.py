"""Create Agent - Build custom voice agents."""

import streamlit as st
from database import get_db_session, create_agent
from agent_system import AgentBuilder, get_available_templates
from utils import show_success, show_error

# Page config
st.set_page_config(
    page_title="Create Agent",
    page_icon="✨",
    layout="wide",
)

# Header
st.title("✨ Create Your Voice Agent")
st.markdown("Build a custom agent for your specific needs")

# Tabs
tab1, tab2 = st.tabs(["🛠️ Custom Agent", "📋 From Template"])

# Tab 1: Custom Agent
with tab1:
    st.markdown("### Build from Scratch")
    
    with st.form("create_agent_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            agent_name = st.text_input(
                "Agent Name *",
                placeholder="e.g., Product Feedback Collector",
                help="A descriptive name for your agent"
            )
            
            category = st.selectbox(
                "Category *",
                AgentBuilder.CATEGORIES,
                help="Select the category that best fits your agent"
            )
            
            tts_voice = st.selectbox(
                "Voice",
                AgentBuilder.AVAILABLE_VOICES,
                help="Select the voice for your agent"
            )
        
        with col2:
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Controls randomness. Lower = more focused, Higher = more creative"
            )
            
            max_tokens = st.number_input(
                "Max Tokens",
                min_value=100,
                max_value=2000,
                value=500,
                step=50,
                help="Maximum length of responses"
            )
        
        description = st.text_area(
            "Description *",
            placeholder="Describe what your agent does...",
            height=100,
            help="A brief description of your agent's purpose"
        )
        
        instructions = st.text_area(
            "Instructions *",
            placeholder="""You are a helpful assistant. Your role is to:
1. Ask the following questions one by one:
   - Question 1
   - Question 2
   - Question 3
2. Acknowledge each response
3. Thank them at the end""",
            height=300,
            help="Detailed instructions for your agent's behavior"
        )
        
        submitted = st.form_submit_button("🚀 Create Agent", use_container_width=True)
        
        if submitted:
            if not agent_name or not description or not instructions:
                show_error("Please fill in all required fields (marked with *)")
            else:
                try:
                    # Create agent using builder
                    builder = AgentBuilder()
                    builder.set_name(agent_name)
                    builder.set_description(description)
                    builder.set_instructions(instructions)
                    builder.set_category(category)
                    builder.set_voice(tts_voice)
                    builder.set_temperature(temperature)
                    builder.set_max_tokens(max_tokens)
                    
                    # Validate
                    is_valid, error = builder.validate()
                    if not is_valid:
                        show_error(error)
                    else:
                        # Save to database
                        config = builder.build()
                        
                        with get_db_session() as session:
                            agent = create_agent(
                                session,
                                name=config["name"],
                                description=config["description"],
                                instructions=config["instructions"],
                                llm_model=config["llm_model"],
                                stt_model=config["stt_model"],
                                tts_voice=config["tts_voice"],
                                temperature=config["temperature"],
                                max_tokens=config["max_tokens"],
                                category=config["category"],
                                is_active=True,
                            )
                        
                        show_success(f"Agent '{agent.name}' created successfully!")
                        st.balloons()
                        
                        # Button to go to marketplace
                        if st.button("Go to Marketplace"):
                            st.switch_page("pages/1_🏪_Agent_Marketplace.py")
                        
                except Exception as e:
                    show_error(f"Error creating agent: {str(e)}")

# Tab 2: From Template
with tab2:
    st.markdown("### Start with a Template")
    st.markdown("Choose a pre-configured template and customize it")
    
    # Get available templates
    templates = get_available_templates()
    
    # Display templates
    for template in templates:
        with st.expander(f"📋 {template['name']}"):
            st.markdown(f"**Category:** {template['category']}")
            st.markdown(f"**Description:** {template['description']}")
            
            if st.button(f"Use this template", key=f"use_template_{template['id']}"):
                try:
                    # Load template
                    from agent_system import create_template_agent
                    config = create_template_agent(template['id'])
                    
                    # Save to database
                    with get_db_session() as session:
                        agent = create_agent(
                            session,
                            name=config["name"],
                            description=config["description"],
                            instructions=config["instructions"],
                            llm_model=config["llm_model"],
                            stt_model=config["stt_model"],
                            tts_voice=config["tts_voice"],
                            temperature=config["temperature"],
                            max_tokens=config["max_tokens"],
                            category=config["category"],
                            is_active=True,
                        )
                    
                    show_success(f"Agent '{agent.name}' created from template!")
                    st.balloons()
                    
                    # Refresh to show new agent
                    st.rerun()
                    
                except Exception as e:
                    show_error(f"Error creating agent from template: {str(e)}")

# Sidebar tips
with st.sidebar:
    st.markdown("### 💡 Tips for Creating Agents")
    
    st.markdown("""
        **Good Instructions:**
        - Be specific about the questions to ask
        - Define the conversation flow
        - Specify the tone and personality
        - Include how to handle different responses
        
        **Example Structure:**
        ```
        You are a [role]. Your goal is to [objective].
        
        Ask these questions:
        1. [Question 1]
        2. [Question 2]
        3. [Question 3]
        
        Guidelines:
        - Acknowledge each response
        - Be [tone: friendly/professional/etc]
        - Ask follow-up questions if needed
        - Thank them at the end
        ```
    """)
    
    st.markdown("---")
    
    st.markdown("### 🎤 Voice Selection")
    st.markdown("""
        Available voices:
        - **tara**: Best overall (default)
        - **leah**: Clear female
        - **leo**: Professional male
        - **dan**: Casual male
        - **jess**, **mia**, **zac**, **zoe**
    """)

