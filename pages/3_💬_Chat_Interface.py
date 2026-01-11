"""Chat Interface - Interact with agents."""

import streamlit as st
import asyncio
from database import get_db_session, get_agent
try:
    from agent_system import TextAgent
    TEXT_AGENT_AVAILABLE = True
except (ImportError, AttributeError):
    TextAgent = None
    TEXT_AGENT_AVAILABLE = False
from conversation import SessionManager, DataCollector, ConversationTracker
from utils import get_or_create_session_state, show_success, show_error, show_info

# Page config
st.set_page_config(
    page_title="Chat Interface",
    page_icon="💬",
    layout="wide",
)

# Initialize session state
get_or_create_session_state("selected_agent_id", None)
get_or_create_session_state("chat_mode", "text")
get_or_create_session_state("chat_history", [])
get_or_create_session_state("session_id", None)
get_or_create_session_state("text_agent", None)
get_or_create_session_state("voice_agent", None)
get_or_create_session_state("conversation_tracker", None)
get_or_create_session_state("last_voice_text", "")

# Check if agent is selected
if not st.session_state.selected_agent_id:
    st.warning("Please select an agent from the marketplace first")
    if st.button("Go to Marketplace"):
        st.switch_page("pages/1_🏪_Agent_Marketplace.py")
    st.stop()

# Load agent from database
try:
    with get_db_session() as session:
        agent_data = get_agent(session, st.session_state.selected_agent_id)
        if not agent_data:
            st.error("Agent not found")
            st.stop()

        agent_dict = agent_data.to_dict()
except Exception as e:
    st.error(f"Error loading agent: {str(e)}")
    st.stop()

# Header
st.title(f"💬 Chat with {agent_dict['name']}")
st.markdown(agent_dict.get('description', 'No description'))

# Mode selector
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    mode = st.radio(
        "Select Mode",
        ["Text Chat", "Voice Chat"],
        horizontal=True,
        index=0 if st.session_state.chat_mode == "text" else 1,
    )
    st.session_state.chat_mode = "text" if mode == "Text Chat" else "voice"

with col3:
    if st.button("🔄 New Conversation"):
        st.session_state.chat_history = []
        st.session_state.session_id = None
        st.session_state.text_agent = None
        st.session_state.voice_agent = None
        st.session_state.conversation_tracker = None
        st.session_state.last_voice_text = ""
        st.rerun()

st.markdown("---")

# Initialize conversation if needed
if not st.session_state.session_id:
    try:
        with get_db_session() as session:
            session_manager = SessionManager(session)
            session_id = session_manager.create_session(
                agent_id=st.session_state.selected_agent_id,
                mode=st.session_state.chat_mode,
            )
            st.session_state.session_id = session_id

            # Get conversation ID
            conversation_id = session_manager.get_conversation_id(session_id)

            # Initialize data collector and tracker
            data_collector = DataCollector(session)
            conversation_tracker = ConversationTracker(
                conversation_id, data_collector)
            st.session_state.conversation_tracker = conversation_tracker

            show_success("Conversation started!")
    except Exception as e:
        show_error(f"Error starting conversation: {str(e)}")
        st.stop()

# TEXT CHAT MODE
if st.session_state.chat_mode == "text":
    # Initialize text agent if needed
    if not st.session_state.text_agent:
        try:
            st.session_state.text_agent = TextAgent.from_db_agent(agent_dict)
        except Exception as e:
            show_error(f"Error initializing agent: {str(e)}")
            st.stop()

    # Chat container
    chat_container = st.container()

    with chat_container:
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message to history
        st.session_state.chat_history.append(
            {"role": "user", "content": prompt})

        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Get agent response
        try:
            with st.spinner("Thinking..."):
                # Get response from agent
                response = asyncio.run(
                    st.session_state.text_agent.chat(prompt))

                # Add to history
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response})

                # Track conversation data
                if st.session_state.conversation_tracker:
                    st.session_state.conversation_tracker.add_user_message(
                        prompt)
                    st.session_state.conversation_tracker.add_agent_message(
                        response)

                # Display agent response
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(response)

        except Exception as e:
            show_error(f"Error: {str(e)}")

# VOICE CHAT MODE
else:
    show_info("Voice mode requires LM Studio running with Orpheus TTS model")

    # Initialize voice agent if needed
    if not st.session_state.get("voice_agent"):
        try:
            from agent_system import VoiceAgentWrapper
            import os

            groq_key = os.getenv("GROQ_API_KEY")
            if not groq_key:
                show_error(
                    "GROQ_API_KEY not found. Please set it in your .env file.")
                st.stop()

            st.session_state.voice_agent = VoiceAgentWrapper(
                name=agent_dict["name"],
                instructions=agent_dict["instructions"],
                groq_api_key=groq_key,
                llm_model=agent_dict.get(
                    "llm_model", "llama-3.3-70b-versatile"),
                stt_model=agent_dict.get("stt_model", "whisper-large-v3"),
                tts_voice=agent_dict.get("tts_voice", "tara"),
                temperature=agent_dict.get("temperature", 0.7),
                max_tokens=agent_dict.get("max_tokens", 500),
            )
            show_success("Voice agent initialized!")
        except Exception as e:
            show_error(f"Error initializing voice agent: {str(e)}")
            st.stop()

    st.markdown("### 🎤 Voice Chat")

    # Chat container for history
    chat_container = st.container()

    with chat_container:
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                # If there's audio, show a play button
                if "audio" in msg and msg["audio"]:
                    st.audio(msg["audio"], format="audio/wav")

    # Audio recording section
    st.markdown("---")

    # Try to use streamlit-audiorecorder if available, otherwise use file upload
    try:
        from audiorecorder import audiorecorder
        import subprocess
        import shutil
        import os

        # Check if ffprobe is available (required by audiorecorder)
        # Try multiple methods to find ffprobe
        ffprobe_available = False
        ffprobe_path = None

        # Method 1: Check if ffprobe is in PATH
        ffprobe_path = shutil.which("ffprobe")

        # Method 2: Try common installation paths (macOS Homebrew)
        if not ffprobe_path:
            common_paths = [
                "/opt/homebrew/bin/ffprobe",  # Apple Silicon Macs
                "/usr/local/bin/ffprobe",     # Intel Macs
                "/usr/bin/ffprobe",
            ]
            for path in common_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    ffprobe_path = path
                    break

        # If we found ffprobe, verify it works (but be lenient - just check if file exists)
        if ffprobe_path:
            try:
                # Just check if we can execute it - don't require version output
                result = subprocess.run(
                    [ffprobe_path, "-version"],
                    capture_output=True,
                    timeout=2,
                    env=os.environ.copy()  # Preserve environment
                )
                # Consider it available if command runs (even if exit code is non-zero)
                ffprobe_available = True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                ffprobe_available = False
        else:
            ffprobe_available = False

        if not ffprobe_available:
            st.warning(
                "⚠️ FFmpeg not found. Audio recording requires FFmpeg. "
                "Install with: `brew install ffmpeg`\n\n"
                "If you already installed it, try restarting Streamlit."
            )

        if ffprobe_available:
            st.markdown("#### 🎤 Record Your Voice")
            # Set PATH to include ffprobe location if needed
            if ffprobe_path and "/opt/homebrew/bin" in ffprobe_path:
                os.environ["PATH"] = "/opt/homebrew/bin:" + \
                    os.environ.get("PATH", "")

            audio_bytes = audiorecorder(
                "Click to record", "Click to stop recording")
        else:
            audio_bytes = b""

        if len(audio_bytes) > 0:
            # Audio was recorded
            try:
                import io
                import soundfile as sf
                import numpy as np

                with st.spinner("🔊 Processing your voice..."):
                    # Convert bytes to numpy array
                    audio_io = io.BytesIO(audio_bytes)
                    audio_data, sample_rate = sf.read(audio_io)

                    # Ensure mono
                    if len(audio_data.shape) > 1:
                        audio_data = np.mean(audio_data, axis=1)

                    # Resample to 16kHz if needed
                    if sample_rate != 16000:
                        from scipy import signal
                        num_samples = int(len(audio_data) *
                                          16000 / sample_rate)
                        audio_data = signal.resample(audio_data, num_samples)

                    # Process through voice agent
                    transcription, response_text, audio_response = asyncio.run(
                        st.session_state.voice_agent.process_audio(
                            audio_data,
                            play_response=False
                        )
                    )

                    # Add user message
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": f"🎤 **[Voice]** {transcription}"
                    })

                    # Add agent response
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response_text if response_text != "(Voice response - audio only)" else "🔊 Voice response",
                        "audio": audio_response if audio_response else None
                    })

                    # Track conversation data
                    if st.session_state.conversation_tracker:
                        st.session_state.conversation_tracker.add_user_message(
                            transcription)
                        st.session_state.conversation_tracker.add_agent_message(
                            response_text)

                    show_success("Voice processed!")
                    st.rerun()

            except Exception as e:
                error_msg = str(e)
                if "ffprobe" in error_msg.lower() or "ffmpeg" in error_msg.lower():
                    show_error(
                        "FFmpeg is required for audio processing. Install with: `brew install ffmpeg`")
                    st.info(
                        "💡 **Alternative**: Use the file upload option below to upload audio files directly.")
                else:
                    show_error(f"Error processing audio: {error_msg}")
                    import traceback
                    st.code(traceback.format_exc())

    except ImportError:
        # Fallback to file upload
        st.markdown("#### 🎤 Upload Audio File")
        st.info(
            "Install streamlit-audiorecorder for in-browser recording: `pip install streamlit-audiorecorder`")

        uploaded_file = st.file_uploader(
            "Upload an audio file (WAV, MP3)", type=["wav", "mp3"])

        if uploaded_file is not None:
            try:
                import io
                import soundfile as sf
                import numpy as np

                with st.spinner("🔊 Processing your audio..."):
                    # Read audio file
                    audio_data, sample_rate = sf.read(
                        io.BytesIO(uploaded_file.read()))

                    # Ensure mono
                    if len(audio_data.shape) > 1:
                        audio_data = np.mean(audio_data, axis=1)

                    # Resample to 16kHz if needed
                    if sample_rate != 16000:
                        from scipy import signal
                        num_samples = int(len(audio_data) *
                                          16000 / sample_rate)
                        audio_data = signal.resample(audio_data, num_samples)

                    # Process through voice agent
                    transcription, response_text, audio_response = asyncio.run(
                        st.session_state.voice_agent.process_audio(
                            audio_data,
                            play_response=False
                        )
                    )

                    # Add user message
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": f"🎤 **[Voice]** {transcription}"
                    })

                    # Add agent response
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response_text if response_text != "(Voice response - audio only)" else "🔊 Voice response",
                        "audio": audio_response if audio_response else None
                    })

                    # Track conversation data
                    if st.session_state.conversation_tracker:
                        st.session_state.conversation_tracker.add_user_message(
                            transcription)
                        st.session_state.conversation_tracker.add_agent_message(
                            response_text)

                    show_success("Audio processed!")
                    st.rerun()

            except Exception as e:
                show_error(f"Error processing audio: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

    st.markdown("---")

    # Text input alternative in voice mode
    st.markdown("#### ⌨️ Or Type Your Message")
    text_input = st.chat_input("Type your message (optional)...")

    if text_input and text_input != st.session_state.get("last_voice_text", ""):
        st.session_state.last_voice_text = text_input

        try:
            with st.spinner("🤖 Thinking..."):
                # Process text through voice agent
                response = asyncio.run(
                    st.session_state.voice_agent.process_text(text_input))

                # Add to history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": text_input
                })
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })

                # Track conversation
                if st.session_state.conversation_tracker:
                    st.session_state.conversation_tracker.add_user_message(
                        text_input)
                    st.session_state.conversation_tracker.add_agent_message(
                        response)

                st.rerun()

        except Exception as e:
            show_error(f"Error: {str(e)}")

# Sidebar - Conversation info
with st.sidebar:
    st.markdown("### 📊 Conversation Info")

    if st.session_state.session_id:
        st.markdown(f"**Session ID:** `{st.session_state.session_id[:8]}...`")
        st.markdown(f"**Mode:** {st.session_state.chat_mode.upper()}")
        st.markdown(f"**Messages:** {len(st.session_state.chat_history)}")

    st.markdown("---")

    st.markdown("### 🎭 Agent Details")
    st.markdown(f"**Voice:** {agent_dict.get('tts_voice', 'N/A')}")
    st.markdown(f"**Model:** {agent_dict.get('llm_model', 'N/A')}")
    st.markdown(f"**Temperature:** {agent_dict.get('temperature', 0.7)}")

    st.markdown("---")

    # Collected data preview
    if st.session_state.conversation_tracker:
        st.markdown("### 📝 Collected Data")

        try:
            with get_db_session() as session:
                from conversation import DataCollector
                collector = DataCollector(session)

                # Get session manager to find conversation ID
                from conversation import SessionManager
                session_mgr = SessionManager(session)
                conversation_id = session_mgr.get_conversation_id(
                    st.session_state.session_id)

                if conversation_id:
                    collected_data = collector.get_conversation_data(
                        conversation_id)

                    if collected_data:
                        st.markdown(f"**Responses:** {len(collected_data)}")

                        with st.expander("View Collected Responses"):
                            for i, item in enumerate(collected_data, 1):
                                st.markdown(
                                    f"**{i}. Q:** {item['question'] or 'N/A'}")
                                st.markdown(f"**A:** {item['answer']}")
                                st.markdown("---")
                    else:
                        st.info("No data collected yet")
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")

    st.markdown("---")

    # End conversation button
    if st.button("🏁 End Conversation", use_container_width=True):
        try:
            with get_db_session() as session:
                from conversation import SessionManager
                session_manager = SessionManager(session)
                session_manager.end_session(st.session_state.session_id)

            show_success("Conversation ended successfully!")

            # Clear session
            st.session_state.chat_history = []
            st.session_state.session_id = None
            st.session_state.text_agent = None
            st.session_state.conversation_tracker = None

            # Option to go to data view
            if st.button("📊 View Collected Data"):
                st.switch_page("pages/4_📊_View_Data.py")

        except Exception as e:
            show_error(f"Error ending conversation: {str(e)}")
