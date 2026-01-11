# 🎙️ Voice Agent Platform

A comprehensive platform for building, deploying, and managing AI voice agents that collect structured data through natural conversations - like Google Forms, but conversational!

Built with **OpenAI Agents SDK**, **Groq AI**, **Streamlit**, and **PostgreSQL/SQLite**.

---

## ✨ Features

### Core Capabilities

-   🤖 **Agent Builder**: Create custom voice agents with 5 pre-built templates
-   🏪 **Agent Marketplace**: Browse and use available agents
-   💬 **Text & Voice Chat**: Interact through text or voice (with LM Studio)
-   📊 **Data Collection**: Automatic Q&A extraction and storage
-   📤 **Excel/CSV Export**: Export data in Google Forms style
-   💾 **Database**: PostgreSQL or SQLite support

### Agent Templates

1. **Startup Validator** - Validate startup ideas
2. **Job Interviewer** - Practice interviews
3. **Customer Service** - Collect feedback
4. **Product Feedback** - Gather user insights
5. **General Survey** - Customizable surveys

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Frontend                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │Marketplace│ │  Create  │ │   Chat   │ │View Data │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└───────────────────┬──────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼──────┐  ┌────▼─────┐  ┌─────▼──────┐
│  Agent   │  │Conversation│  │   Export   │
│  System  │  │Management │  │   System   │
└────┬─────┘  └─────┬──────┘  └─────┬──────┘
     │              │               │
     └──────────────┼───────────────┘
                    │
            ┌───────▼────────┐
            │    Database    │
            │(PostgreSQL or  │
            │    SQLite)     │
            └────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

-   Python 3.10+
-   UV package manager (or pip)
-   Groq API key ([Get one here](https://console.groq.com))
-   PostgreSQL (optional - SQLite works for development)
-   LM Studio (optional - only for voice mode)

### Installation

```bash
# 1. Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
uv pip install -e .
# Or with pip: pip install -r requirements.txt

# 3. Create .env file
cat > .env << 'EOF'
# Required: Groq API Key
GROQ_API_KEY=your_groq_api_key_here

# Optional: Database (defaults to SQLite)
DATABASE_URL=sqlite:///./voiceagent.db

# Optional: LM Studio for voice mode
LM_STUDIO_URL=http://localhost:1234/v1
EOF

# 4. Initialize database and create sample agents
python3 init_platform.py

# 5. Start the platform
streamlit run app.py
```

**Access at:** http://localhost:8501

---

## 💻 Technology Stack

### Backend

-   **OpenAI Agents SDK** - Agent framework
-   **Groq API** - Whisper STT & Llama LLM
-   **SQLAlchemy** - Database ORM
-   **PostgreSQL/SQLite** - Data storage
-   **Pandas** - Data export

### Frontend

-   **Streamlit** - Web interface
-   **Python** - Core logic

### Voice (Optional)

-   **LM Studio** - Local model runtime
-   **Orpheus TTS** - Text-to-speech
-   **Groq Whisper** - Speech-to-text

---

## 📖 Usage Guide

### 1. Browse Agents

-   Go to **🏪 Agent Marketplace**
-   Browse available agents
-   Click "Start Text Chat" or "Start Voice Chat"

### 2. Create Custom Agent

-   Go to **✨ Create Agent**
-   Choose "Custom Agent" or "From Template"
-   Fill in:
    -   Name and description
    -   Instructions (system prompt)
    -   Voice selection
    -   Temperature and max tokens
-   Click "Create Agent"

#### Example Agent Instructions:

```
You are a startup advisor. Ask these questions one by one:

1. What problem does your startup solve?
2. Who are your target customers?
3. What makes your solution unique?
4. How will you make money?
5. What is your go-to-market strategy?

After each answer:
- Acknowledge their response
- Provide brief feedback
- Ask the next question

Be encouraging and helpful.
```

### 3. Chat with Agent

-   Select an agent from Marketplace
-   Choose Text or Voice mode
-   Answer the agent's questions
-   Data is collected automatically

### 4. View & Export Data

-   Go to **📊 View Data**
-   Select an agent
-   View responses in different formats:
    -   All Responses
    -   By Conversation
    -   Statistics
-   Export to Excel/CSV (Google Forms style)

---

## 🗄️ Database Setup

### SQLite (Default)

No setup needed! Works out of the box.

```env
DATABASE_URL=sqlite:///./voiceagent.db
```

### PostgreSQL (Production)

**Local PostgreSQL:**

```bash
# Install PostgreSQL
brew install postgresql  # macOS
# or: sudo apt install postgresql  # Ubuntu

# Create database
createdb voiceagent

# Update .env
DATABASE_URL=postgresql://username:password@localhost:5432/voiceagent
```

**Cloud PostgreSQL (Free Tiers):**

-   **Supabase**: https://supabase.com
-   **Railway**: https://railway.app
-   **Render**: https://render.com

---

## 🎤 Voice Mode Setup (Optional)

Voice mode requires LM Studio with Orpheus TTS:

### 1. Download LM Studio

https://lmstudio.ai/

### 2. Download Orpheus Model

-   Search: `lex-au/Orpheus-3b-FT-Q4_K_M.gguf`
-   Download the model

### 3. Start Server

-   Load Orpheus model in LM Studio
-   Start local server (default: http://localhost:1234/v1)

### 4. Configure

```env
LM_STUDIO_URL=http://localhost:1234/v1
```

**Note**: Voice mode is optional. Text mode works without LM Studio.

---

## 📂 Project Structure

```
VoiceAgent/
├── app.py                          # Main Streamlit app
├── pages/                          # Streamlit pages
│   ├── 1_🏪_Agent_Marketplace.py
│   ├── 2_✨_Create_Agent.py
│   ├── 3_💬_Chat_Interface.py
│   └── 4_📊_View_Data.py
├── database/                       # Database layer
│   ├── models.py                   # SQLAlchemy models
│   ├── connection.py               # DB connection
│   └── operations.py               # CRUD operations
├── agent_system/                   # Agent management
│   ├── agent_builder.py            # Build agents
│   ├── text_agent.py               # Text agent
│   └── voice_agent_wrapper.py     # Voice integration
├── conversation/                   # Session tracking
│   ├── session_manager.py
│   └── data_collector.py
├── export/                         # Data export
│   └── excel_exporter.py
├── utils/                          # Utilities
│   └── streamlit_helpers.py
├── src/voiceagent/                # Original voice agent
│   ├── core/
│   ├── models/
│   └── config/
├── init_platform.py               # Initialization script
├── requirements.txt               # Dependencies
├── pyproject.toml                 # UV config
└── README.md                      # This file
```

---

## 🔧 Configuration

All settings via `.env`:

```env
# API Configuration
GROQ_API_KEY=your_key                          # Required
LM_STUDIO_URL=http://localhost:1234/v1        # Optional

# Database
DATABASE_URL=sqlite:///./voiceagent.db        # SQLite (default)
# DATABASE_URL=postgresql://user:pass@host/db  # PostgreSQL

# Models
STT_MODEL=whisper-large-v3                    # Speech-to-text
LLM_MODEL=llama-3.3-70b-versatile             # LLM
TTS_VOICE=tara                                # Voice (tara, leah, leo, etc.)

# Agent Defaults
TEMPERATURE=0.7
MAX_TOKENS=500
```

---

## 🎯 Use Cases

-   **Startup Validation**: Validate ideas through structured questions
-   **Job Interviews**: Practice interview skills
-   **Customer Feedback**: Collect satisfaction data
-   **Market Research**: Conduct surveys
-   **User Testing**: Get product feedback
-   **Education**: Create assessments and tutors

---

## 📊 Data Export

### Export Formats

**Long Format** (Default):

```
Conversation ID | Session ID | Question | Answer | Timestamp
001             | abc123     | Q1       | A1     | 2026-01-11
001             | abc123     | Q2       | A2     | 2026-01-11
```

**Wide Format** (Google Forms style):

```
Conversation ID | Started At | Q1 | Q2 | Q3
001             | 2026-01-11 | A1 | A2 | A3
002             | 2026-01-11 | A1 | A2 | A3
```

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
python3 -c "from database import init_db; init_db()"
```

### Streamlit Not Starting

```bash
pip list | grep streamlit
# If missing: pip install streamlit
```

### Voice Mode Not Working

Requires LM Studio with Orpheus model running locally.

### Missing Dependencies

```bash
uv pip install --force-reinstall -e .
```

---

## 🚀 Deployment

### Streamlit Community Cloud

1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Add `.env` secrets
4. Deploy!

### Docker

```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["streamlit", "run", "app.py"]
```

---

## 🤝 Contributing

This is a complete platform implementation. Feel free to:

-   Add more agent templates
-   Improve the UI/UX
-   Add more export formats
-   Implement analytics dashboards
-   Add user authentication

---

## 📝 License

MIT License - Use freely in your projects!

---

## 🙏 Credits

Built with:

-   **OpenAI Agents SDK** - Agent framework
-   **Groq** - Fast Whisper STT and Llama LLM
-   **Orpheus TTS** - High-quality voice synthesis
-   **Streamlit** - Beautiful web framework
-   **PostgreSQL** - Robust database
-   **SQLAlchemy** - Database ORM

---

## 📞 Support

### Quick Test

```bash
python3 init_platform.py  # Initialize platform
streamlit run app.py      # Start application
```

### System Info

Check `.env` configuration and ensure GROQ_API_KEY is set.

---

**Need Help?**

1. Ensure `.env` is configured
2. Run `python3 init_platform.py`
3. Start with `streamlit run app.py`
4. Access at http://localhost:8501

**Happy Building! 🎉**
