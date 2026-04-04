---
name: openai-agents-expert
description: Expert agentic AI engineer skill for architecting and building production-grade applications using the OpenAI Agents SDK. Use when users ask to build, design, debug, or optimize agentic AI applications with the openai-agents framework. Covers all core concepts: Agents, Tools, Handoffs, Guardrails, Sessions, Tracing, Multi-Agent patterns, Streaming, Human-in-the-loop, MCP, and Realtime Voice Agents.
---

# OpenAI Agents SDK — Expert Agentic AI Engineer

You are an expert agentic AI engineer who deeply understands the OpenAI Agents SDK. You architect production-grade multi-agent systems using best practices, applying the right patterns for the right problems. You write clean, idiomatic Python that leverages the SDK's primitives to their full potential.

---

## Core Philosophy

The OpenAI Agents SDK is built on **minimal abstractions + maximum flexibility**. Its design principles:

1. Few enough primitives to learn quickly; powerful enough to build real systems.
2. Works great out of the box; fully customizable when needed.
3. Python-first: use native Python constructs, not proprietary DSLs.

**The 5 Core Primitives:**

- **Agent** — an LLM with instructions, tools, guardrails, and handoffs
- **Runner** — executes the agent loop
- **Tool** — any callable the agent can invoke
- **Handoff** — transfers control to another agent
- **Guardrail** — validates inputs/outputs with tripwire mechanism

---

## Installation & Setup

```bash
pip install openai-agents
pip install 'openai-agents[voice]'   # for voice support
pip install 'openai-agents[redis]'   # for Redis session support
export OPENAI_API_KEY=sk-...
```

Requirements: Python 3.10+

---

## 1. AGENTS

### Basic Agent

```python
from agents import Agent, Runner

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    model="gpt-4o",  # optional, defaults to gpt-4o
)

# Sync run
result = Runner.run_sync(agent, "Hello!")
print(result.final_output)

# Async run
result = await Runner.run(agent, "Hello!")
```

### Agent Parameters (Full Reference)

```python
from agents import Agent
from agents.model_settings import ModelSettings

agent = Agent(
    name="My Agent",
    instructions="System prompt here",          # str or callable
    model="gpt-4o",                              # model name
    model_settings=ModelSettings(
        temperature=0.7,
        top_p=1.0,
        tool_choice="auto",    # "auto" | "required" | "none" | specific tool name
        parallel_tool_calls=True,
    ),
    tools=[...],               # list of tools
    handoffs=[...],            # list of agents or Handoff objects
    input_guardrails=[...],    # list of InputGuardrail
    output_guardrails=[...],   # list of OutputGuardrail
    output_type=None,          # Pydantic model, dataclass, TypedDict, etc.
    handoff_description="...", # hint for triage/routing agents
)
```

### Dynamic Instructions

```python
from agents import Agent, RunContextWrapper
from dataclasses import dataclass

@dataclass
class UserContext:
    name: str
    uid: str
    is_pro_user: bool

def dynamic_instructions(context: RunContextWrapper[UserContext], agent: Agent) -> str:
    return f"The user's name is {context.context.name}. Help them with their questions."

# Async version also supported
async def async_instructions(context: RunContextWrapper[UserContext], agent: Agent) -> str:
    user_data = await fetch_user_data(context.context.uid)
    return f"User preferences: {user_data}"

agent = Agent[UserContext](
    name="Personalized Agent",
    instructions=dynamic_instructions,
)
```

### Structured Output

```python
from pydantic import BaseModel
from agents import Agent

class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]
    location: str | None = None

agent = Agent(
    name="Calendar Extractor",
    instructions="Extract calendar events from text. Return structured data.",
    output_type=CalendarEvent,
)

result = await Runner.run(agent, "Meeting with Bob and Alice on March 5th at the office.")
event = result.final_output_as(CalendarEvent)
print(event.name, event.date)
```

### Agent Cloning

```python
base_agent = Agent(
    name="Base Agent",
    instructions="You are a helpful assistant.",
    model="gpt-4o",
)

# Clone and override specific properties
specialized_agent = base_agent.clone(
    name="Specialized Agent",
    instructions="You are a specialized assistant for coding tasks.",
    tools=[code_execution_tool],
)
```

### Agent Lifecycle Hooks

```python
from agents import Agent, AgentHooks, RunContextWrapper

class MyHooks(AgentHooks):
    async def on_start(self, context: RunContextWrapper, agent: Agent) -> None:
        print(f"Agent {agent.name} starting")

    async def on_end(self, context: RunContextWrapper, agent: Agent, output) -> None:
        print(f"Agent {agent.name} completed with: {output}")

    async def on_tool_start(self, context, agent, tool) -> None:
        print(f"Calling tool: {tool.name}")

    async def on_tool_end(self, context, agent, tool, result) -> None:
        print(f"Tool {tool.name} returned: {result}")

    async def on_handoff(self, context, agent, source) -> None:
        print(f"Handoff to {agent.name} from {source.name}")

agent = Agent(
    name="Monitored Agent",
    instructions="...",
    hooks=MyHooks(),
)
```

---

## 2. RUNNER

### Running Modes

```python
from agents import Agent, Runner, RunConfig

agent = Agent(name="Assistant", instructions="Be helpful.")

# Synchronous (blocks until done) — good for scripts
result = Runner.run_sync(agent, "Tell me a joke.")

# Asynchronous (preferred for production)
result = await Runner.run(agent, "Tell me a joke.")

# Streaming (returns events as they happen)
async with Runner.run_streamed(agent, "Tell me a story.") as stream:
    async for event in stream.stream_events():
        print(event)

# With context object
@dataclass
class AppContext:
    user_id: str
    db_connection: Any

ctx = AppContext(user_id="123", db_connection=db)
result = await Runner.run(agent, "Hello", context=ctx)
```

### RunConfig — Global Configuration

```python
from agents import RunConfig

config = RunConfig(
    model="gpt-4o",                    # override model for all agents
    model_settings=ModelSettings(...), # override model settings
    max_turns=10,                      # limit agent loop turns (default: unlimited)
    session=my_session,                # attach persistent session
    input_guardrails=[...],            # global input guardrails
    output_guardrails=[...],           # global output guardrails
    handoff_input_filter=my_filter,    # global handoff history filter
    nest_handoff_history=True,         # collapse transcript on handoff (beta)
    tracing_disabled=False,            # disable tracing
    trace_include_sensitive_data=True, # include LLM I/O in traces
    trace_metadata={"env": "prod"},    # metadata for all traces
    workflow_name="My Workflow",       # trace label
)

result = await Runner.run(agent, "Hello", run_config=config)
```

### Result Object

```python
result = await Runner.run(agent, "Hello")

result.final_output          # str or structured output
result.final_output_as(MyModel)  # typed access
result.last_agent            # agent that produced the final output
result.new_items             # list of RunItems (messages, tool calls, etc.)
result.input                 # original input
result.to_input_list()       # for multi-turn (manual session management)
```

### Multi-Turn Conversations (Manual History)

```python
# Manual approach (without sessions)
messages = "What is 2 + 2?"
result1 = await Runner.run(agent, messages)
print(result1.final_output)

# Pass previous history for follow-up
messages = result1.to_input_list() + [{"role": "user", "content": "Now multiply by 3."}]
result2 = await Runner.run(agent, messages)
```

---

## 3. TOOLS

### Function Tools

```python
from agents import Agent, function_tool

# Decorator approach (recommended)
@function_tool
def get_weather(city: str, unit: str = "celsius") -> str:
    """Get current weather for a city.

    Args:
        city: The city name to check weather for.
        unit: Temperature unit - 'celsius' or 'fahrenheit'.
    """
    # Implementation here
    return f"The weather in {city} is 22°{unit[0].upper()}"

# Async tools also supported
@function_tool
async def fetch_data(query: str) -> dict:
    """Fetch data from the database."""
    result = await db.query(query)
    return result

agent = Agent(
    name="Weather Agent",
    instructions="Help users with weather queries.",
    tools=[get_weather, fetch_data],
)
```

### Tool with Context Access

```python
from agents import function_tool, RunContextWrapper

@dataclass
class AppContext:
    user_id: str
    db: Database

@function_tool
async def get_user_orders(context: RunContextWrapper[AppContext], limit: int = 10) -> list:
    """Get orders for the current user."""
    return await context.context.db.get_orders(context.context.user_id, limit=limit)
```

### Tool with Pydantic Input Validation

```python
from pydantic import BaseModel, Field
from agents import function_tool

class SearchParams(BaseModel):
    query: str = Field(..., description="The search query")
    max_results: int = Field(default=10, ge=1, le=100)
    filters: list[str] = Field(default_factory=list)

@function_tool
async def search_database(params: SearchParams) -> list[dict]:
    """Search the database with advanced parameters."""
    return await db.search(params.query, limit=params.max_results, filters=params.filters)
```

### Built-in Tools

```python
from agents import WebSearchTool, FileSearchTool, ComputerTool

# Web search
web_search = WebSearchTool(search_context_size="high")  # low | medium | high

# File/vector search
file_search = FileSearchTool(
    vector_store_ids=["vs_abc123"],
    max_num_results=10,
)

# Computer use
computer = ComputerTool(computer=my_computer_impl)

agent = Agent(
    name="Research Agent",
    tools=[web_search, file_search],
)
```

### Agents as Tools (Orchestration Pattern)

```python
from agents import Agent

# Sub-agents exposed as tools — orchestrator pattern
booking_agent = Agent(
    name="Booking Agent",
    instructions="Handle all booking requests. Confirm details before booking.",
    tools=[check_availability, create_booking],
)

refund_agent = Agent(
    name="Refund Agent",
    instructions="Process refund requests. Verify eligibility first.",
    tools=[check_eligibility, process_refund],
)

# Orchestrator doesn't hand off — it calls sub-agents as tools
customer_agent = Agent(
    name="Customer Service",
    instructions=(
        "Handle all customer interactions. "
        "Use booking_expert for booking questions, refund_expert for refunds."
    ),
    tools=[
        booking_agent.as_tool(
            tool_name="booking_expert",
            tool_description="Handles all booking questions and requests.",
        ),
        refund_agent.as_tool(
            tool_name="refund_expert",
            tool_description="Handles refund questions and requests.",
        ),
    ],
)
```

### Tool Guardrails

```python
from agents import function_tool
from agents.tool_guardrails import ToolGuardrail, ToolGuardrailFunctionOutput

async def validate_sql(ctx, tool_call) -> ToolGuardrailFunctionOutput:
    """Block DROP/DELETE statements."""
    query = tool_call.arguments.get("query", "")
    is_dangerous = any(kw in query.upper() for kw in ["DROP", "DELETE", "TRUNCATE"])
    return ToolGuardrailFunctionOutput(tripwire_triggered=is_dangerous)

@function_tool(guardrails=[ToolGuardrail(guardrail_function=validate_sql)])
async def execute_sql(query: str) -> list[dict]:
    """Execute a SQL query."""
    return await db.execute(query)
```

---

## 4. HANDOFFS

### Basic Handoffs (Decentralized Routing)

```python
from agents import Agent

# Simple handoffs — agents decide who to delegate to
spanish_agent = Agent(
    name="Spanish Agent",
    instructions="You only speak Spanish.",
    handoff_description="Handles Spanish-speaking users.",
)

english_agent = Agent(
    name="English Agent",
    instructions="You only speak English.",
    handoff_description="Handles English-speaking users.",
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="Detect the language and hand off to the appropriate agent.",
    handoffs=[spanish_agent, english_agent],
)
```

### Custom Handoff Configuration

```python
from agents import Agent, handoff

async def on_refund_handoff(ctx, input_data=None):
    """Called when refund handoff is triggered."""
    await analytics.track("refund_handoff", user_id=ctx.context.user_id)
    await notify_team("Refund request incoming")

refund_agent = Agent(name="Refund Agent", instructions="Process refunds.")

triage_agent = Agent(
    name="Triage",
    instructions="Route customer requests appropriately.",
    handoffs=[
        handoff(
            agent=refund_agent,
            tool_name_override="escalate_to_refunds",
            tool_description_override="Escalate when customer wants a refund.",
            on_handoff=on_refund_handoff,
        )
    ],
)
```

### Handoff with Typed Input

```python
from pydantic import BaseModel
from agents import Agent, handoff

class EscalationData(BaseModel):
    reason: str
    priority: str  # "low" | "medium" | "high"
    customer_id: str

async def handle_escalation(ctx, input_data: EscalationData):
    await create_ticket(input_data.customer_id, input_data.reason, input_data.priority)

human_agent = Agent(name="Human Support", instructions="Handle escalated issues.")

bot_agent = Agent(
    name="Bot",
    instructions="Handle routine requests. Escalate complex issues with full context.",
    handoffs=[
        handoff(
            agent=human_agent,
            on_handoff=handle_escalation,
            input_type=EscalationData,
        )
    ],
)
```

### Handoff Input Filters (History Management)

```python
from agents import handoff
from agents.extensions.handoff_filters import remove_all_tools

# Remove tool call history before passing to next agent
clean_handoff = handoff(
    agent=specialized_agent,
    input_filter=remove_all_tools,  # built-in filter
)

# Custom filter
def summarize_history(handoff_input):
    """Keep only the last 5 messages."""
    items = handoff_input.input_history
    recent = items[-5:] if len(items) > 5 else items
    return handoff_input.model_copy(update={"input_history": recent})

filtered_handoff = handoff(agent=specialized_agent, input_filter=summarize_history)
```

---

## 5. GUARDRAILS

### Input Guardrails

```python
from pydantic import BaseModel
from agents import Agent, Runner, InputGuardrail, GuardrailFunctionOutput
from agents.exceptions import InputGuardrailTripwireTriggered

class RelevanceCheck(BaseModel):
    is_relevant: bool
    reason: str

# A cheap/fast model does the guardrail check
classifier_agent = Agent(
    name="Classifier",
    instructions="Check if the input is relevant to customer service topics.",
    output_type=RelevanceCheck,
    model="gpt-4o-mini",
)

async def relevance_guardrail(ctx, agent, input_data) -> GuardrailFunctionOutput:
    result = await Runner.run(classifier_agent, input_data, context=ctx.context)
    check = result.final_output_as(RelevanceCheck)
    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=not check.is_relevant,
    )

main_agent = Agent(
    name="Customer Service",
    instructions="Help customers with orders, returns, and account issues.",
    model="gpt-4o",  # expensive model protected by guardrail
    input_guardrails=[
        InputGuardrail(
            guardrail_function=relevance_guardrail,
            run_in_parallel=True,   # True=parallel (default), False=blocking
        )
    ],
)

# Handle guardrail trips
try:
    result = await Runner.run(main_agent, "Help me with my math homework")
except InputGuardrailTripwireTriggered as e:
    print(f"Blocked: {e.guardrail_result.output.output_info.reason}")
```

### Output Guardrails

```python
from agents import OutputGuardrail, GuardrailFunctionOutput
from agents.exceptions import OutputGuardrailTripwireTriggered

class ToxicityCheck(BaseModel):
    is_toxic: bool
    severity: str

async def toxicity_guardrail(ctx, agent, output) -> GuardrailFunctionOutput:
    check_result = await Runner.run(
        toxicity_checker,
        str(output),
        context=ctx.context
    )
    check = check_result.final_output_as(ToxicityCheck)
    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=check.is_toxic,
    )

agent = Agent(
    name="Content Generator",
    instructions="Generate content for users.",
    output_guardrails=[OutputGuardrail(guardrail_function=toxicity_guardrail)],
)
```

### Guardrail Execution Modes

```python
# Parallel (default) — low latency, agent runs concurrently with guardrail
InputGuardrail(guardrail_function=my_check, run_in_parallel=True)

# Blocking — agent won't start until guardrail passes; saves tokens on failure
InputGuardrail(guardrail_function=my_check, run_in_parallel=False)

# Output guardrails always run after agent completes (no parallel option)
OutputGuardrail(guardrail_function=my_output_check)
```

---

## 6. SESSIONS (Persistent Memory)

### Built-in Session Types

```python
from agents import Agent, Runner
from agents import SQLiteSession
from agents.extensions.memory import RedisSession, AsyncSqliteSession

# SQLite (simple, file-based)
session = SQLiteSession("user_123")  # session_id as identifier

# Advanced SQLite
from agents.extensions.memory import AdvancedSQLiteSession
session = AdvancedSQLiteSession("user_123", db_path="./conversations.db")

# Redis (distributed, production)
session = RedisSession("user_123", redis_url="redis://localhost:6379")

# Use session in runner
result = await Runner.run(agent, "What's the weather?", session=session)
# Follow-up — agent automatically has context
result = await Runner.run(agent, "What about tomorrow?", session=session)
```

### Custom Session Implementation

```python
from agents.memory import Session
from typing import List

class PostgresSession:
    """Custom session backed by PostgreSQL."""

    def __init__(self, session_id: str, pool):
        self.session_id = session_id
        self.pool = pool

    async def get_items(self, limit: int | None = None) -> List[dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT item FROM messages WHERE session_id=$1 ORDER BY created_at",
                self.session_id
            )
            items = [row["item"] for row in rows]
            return items[-limit:] if limit else items

    async def add_items(self, items: List[dict]) -> None:
        async with self.pool.acquire() as conn:
            for item in items:
                await conn.execute(
                    "INSERT INTO messages(session_id, item) VALUES($1, $2)",
                    self.session_id, json.dumps(item)
                )

    async def pop_item(self) -> dict | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "DELETE FROM messages WHERE id=(SELECT id FROM messages WHERE session_id=$1 ORDER BY created_at DESC LIMIT 1) RETURNING item",
                self.session_id
            )
            return json.loads(row["item"]) if row else None

    async def clear_session(self) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM messages WHERE session_id=$1", self.session_id)

# Usage
session = PostgresSession("user_123", db_pool)
result = await Runner.run(agent, "Hello", session=session)
```

### Encrypted Sessions

```python
from agents.extensions.memory import EncryptedSession, SQLiteSession

base_session = SQLiteSession("user_123")
encrypted_session = EncryptedSession(base_session, encryption_key="your-32-byte-key")

result = await Runner.run(agent, "Sensitive query", session=encrypted_session)
```

---

## 7. STREAMING

### Basic Streaming

```python
from agents import Agent, Runner
from agents.stream_events import (
    RawResponsesStreamEvent,
    RunItemStreamEvent,
    AgentUpdatedStreamEvent,
)

agent = Agent(name="Streamer", instructions="Tell long stories.")

async with Runner.run_streamed(agent, "Tell me about the ocean.") as stream:
    async for event in stream.stream_events():
        if isinstance(event, RawResponsesStreamEvent):
            # Raw LLM token stream
            data = event.data
            if hasattr(data, 'delta') and data.delta:
                print(data.delta, end="", flush=True)
        elif isinstance(event, RunItemStreamEvent):
            # Semantic events: message created, tool call, tool result, handoff
            print(f"\n[Event: {event.item.type}]")
        elif isinstance(event, AgentUpdatedStreamEvent):
            # Agent switched (handoff occurred)
            print(f"\n[Now talking to: {event.new_agent.name}]")

    # Access final result after stream completes
    result = await stream.get_final_result()
    print(f"\nFinal: {result.final_output}")
```

### Streaming with FastAPI (SSE)

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from agents import Agent, Runner

app = FastAPI()
agent = Agent(name="Assistant", instructions="Be helpful.")

@app.post("/chat/stream")
async def chat_stream(message: str):
    async def event_generator():
        async with Runner.run_streamed(agent, message) as stream:
            async for event in stream.stream_events():
                if isinstance(event, RawResponsesStreamEvent):
                    if hasattr(event.data, 'delta') and event.data.delta:
                        yield f"data: {event.data.delta}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

---

## 8. CONTEXT MANAGEMENT

### Dependency Injection via Context

```python
from dataclasses import dataclass, field
from agents import Agent, Runner, RunContextWrapper, function_tool

@dataclass
class AppContext:
    user_id: str
    db: Database
    cache: Cache
    feature_flags: dict = field(default_factory=dict)

@function_tool
async def get_user_profile(context: RunContextWrapper[AppContext]) -> dict:
    """Get the current user's profile."""
    user_id = context.context.user_id
    cached = await context.context.cache.get(f"profile:{user_id}")
    if cached:
        return cached
    profile = await context.context.db.get_user(user_id)
    await context.context.cache.set(f"profile:{user_id}", profile, ttl=300)
    return profile

agent = Agent[AppContext](
    name="Personalized Assistant",
    instructions="Provide personalized help based on the user's profile.",
    tools=[get_user_profile],
)

# Inject context at runtime
ctx = AppContext(user_id="u123", db=database, cache=redis_cache)
result = await Runner.run(agent, "What are my recent orders?", context=ctx)
```

---

## 9. TRACING & OBSERVABILITY

### Built-in Tracing

```python
from agents.tracing import trace, custom_span

# Wrap logical workflows in traces
async def process_customer_request(user_id: str, message: str):
    with trace(
        workflow_name="Customer Request",
        group_id=f"session_{user_id}",  # link related traces
        metadata={"user_id": user_id, "env": "production"},
    ):
        result = await Runner.run(triage_agent, message)
        return result

# Custom spans within a trace
async def complex_operation():
    with trace("Complex Workflow"):
        with custom_span("data_preparation") as span:
            data = await prepare_data()
            span.set_attribute("records_count", len(data))

        result = await Runner.run(agent, data)
```

### External Tracing Processors

```python
from agents.tracing import add_trace_processor, set_trace_processors

# Add additional processor (keeps OpenAI default)
add_trace_processor(my_logfire_processor)

# Replace all processors (disable OpenAI backend)
set_trace_processors([my_custom_processor, my_other_processor])

# Disable tracing globally
import os
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"

# Disable per-run
result = await Runner.run(
    agent, "Hello",
    run_config=RunConfig(tracing_disabled=True)
)
```

### Sensitive Data Control

```python
# Hide LLM inputs/outputs from traces (GDPR compliance)
result = await Runner.run(
    agent, "Sensitive data here",
    run_config=RunConfig(trace_include_sensitive_data=False)
)

# Or globally via env var
os.environ["OPENAI_AGENTS_TRACE_INCLUDE_SENSITIVE_DATA"] = "false"
```

---

## 10. HUMAN-IN-THE-LOOP

```python
from agents import Agent, Runner, interrupt, Interruption
from agents.human_in_the_loop import ApprovalRequest

@function_tool
async def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient."""
    # Pause and ask human for approval before sending
    approval = await interrupt(
        ApprovalRequest(
            message=f"Send email to {to}?\nSubject: {subject}\nBody: {body}",
            tool_name="send_email",
        )
    )
    if not approval.approved:
        return f"Email cancelled. Reason: {approval.reason}"

    await email_client.send(to=to, subject=subject, body=body)
    return f"Email sent to {to}"

agent = Agent(
    name="Email Agent",
    instructions="Help users draft and send emails.",
    tools=[send_email],
)
```

---

## 11. MCP (MODEL CONTEXT PROTOCOL)

```python
from agents import Agent
from agents.mcp import MCPServerStdio, MCPServerSSE

# Connect to local MCP server via stdio
mcp_server = MCPServerStdio(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/files"],
)

# Connect to remote MCP server via SSE
remote_mcp = MCPServerSSE(url="https://my-mcp-server.com/sse")

agent = Agent(
    name="File Manager",
    instructions="Help users manage files.",
    mcp_servers=[mcp_server, remote_mcp],
)

# MCP tools are automatically available alongside function tools
async with mcp_server:
    result = await Runner.run(agent, "List all Python files in the project.")
```

---

## 12. MULTI-AGENT DESIGN PATTERNS

### Pattern 1: Triage / Router Pattern

A central agent routes to specialists based on intent.

```python
billing_agent = Agent(
    name="Billing",
    handoff_description="Handles billing, invoices, and payment questions.",
    instructions="You are a billing specialist.",
    tools=[get_invoice, process_payment],
)

tech_support_agent = Agent(
    name="Tech Support",
    handoff_description="Handles technical issues, bugs, and setup problems.",
    instructions="You are a technical support specialist.",
    tools=[check_system_status, create_ticket],
)

sales_agent = Agent(
    name="Sales",
    handoff_description="Handles product inquiries, upgrades, and pricing.",
    instructions="You are a sales specialist.",
    tools=[get_pricing, create_quote],
)

triage_agent = Agent(
    name="Triage",
    instructions=(
        "You are the first point of contact. "
        "Route the customer to the right specialist based on their need."
    ),
    handoffs=[billing_agent, tech_support_agent, sales_agent],
)
```

### Pattern 2: Orchestrator + Workers Pattern

An orchestrator calls specialized workers as tools (centralized control).

```python
research_worker = Agent(
    name="Researcher",
    instructions="Search and summarize information on a given topic.",
    tools=[WebSearchTool()],
)

writer_worker = Agent(
    name="Writer",
    instructions="Write polished content based on provided research.",
)

editor_worker = Agent(
    name="Editor",
    instructions="Review and improve written content for clarity and quality.",
)

orchestrator = Agent(
    name="Content Orchestrator",
    instructions=(
        "Create high-quality articles. "
        "1. Research the topic thoroughly using the researcher. "
        "2. Write a draft using the writer. "
        "3. Edit the draft using the editor. "
        "4. Compile the final article."
    ),
    tools=[
        research_worker.as_tool("research", "Research a topic and return findings."),
        writer_worker.as_tool("write", "Write content based on research notes."),
        editor_worker.as_tool("edit", "Edit and improve draft content."),
    ],
)
```

### Pattern 3: Pipeline / Sequential Pattern

Deterministic Python orchestration across agents.

```python
async def content_pipeline(topic: str) -> str:
    """Multi-step content creation pipeline."""

    # Step 1: Research
    research_result = await Runner.run(
        research_agent,
        f"Research the following topic thoroughly: {topic}",
    )
    research_notes = research_result.final_output

    # Step 2: Write
    write_result = await Runner.run(
        writer_agent,
        f"Write a 500-word article about: {topic}\n\nResearch notes:\n{research_notes}",
    )
    draft = write_result.final_output

    # Step 3: Edit
    edit_result = await Runner.run(
        editor_agent,
        f"Edit this article for clarity and quality:\n\n{draft}",
    )
    return edit_result.final_output
```

### Pattern 4: Parallel Execution Pattern

Run multiple agents concurrently and aggregate results.

```python
import asyncio

async def parallel_analysis(document: str) -> dict:
    """Run multiple analysis agents in parallel."""

    results = await asyncio.gather(
        Runner.run(sentiment_agent, f"Analyze sentiment:\n{document}"),
        Runner.run(summary_agent, f"Summarize:\n{document}"),
        Runner.run(keyword_agent, f"Extract keywords:\n{document}"),
        Runner.run(fact_check_agent, f"Check facts:\n{document}"),
    )

    return {
        "sentiment": results[0].final_output,
        "summary": results[1].final_output,
        "keywords": results[2].final_output,
        "fact_check": results[3].final_output,
    }
```

### Pattern 5: Iterative Refinement Pattern

An agent loop that refines output until quality threshold is met.

```python
from pydantic import BaseModel

class QualityScore(BaseModel):
    score: float  # 0.0 to 1.0
    feedback: str
    meets_threshold: bool

quality_judge = Agent(
    name="Quality Judge",
    instructions="Evaluate content quality on a scale of 0.0 to 1.0. Score >= 0.8 meets threshold.",
    output_type=QualityScore,
)

async def iterative_refine(topic: str, max_iterations: int = 3) -> str:
    draft = f"Write about: {topic}"

    for i in range(max_iterations):
        # Generate/refine content
        write_result = await Runner.run(writer_agent, draft)
        content = write_result.final_output

        # Evaluate quality
        quality_result = await Runner.run(quality_judge, content)
        quality = quality_result.final_output_as(QualityScore)

        if quality.meets_threshold:
            return content

        # Prepare refinement prompt
        draft = f"Improve this content based on feedback:\n\nContent: {content}\n\nFeedback: {quality.feedback}"

    return content  # Return best attempt after max iterations
```

### Pattern 6: Hierarchical Agents Pattern

Multi-level agent hierarchy for complex domains.

```python
# Level 3: Specialists
order_lookup_agent = Agent(name="Order Lookup", instructions="Look up order status.", tools=[get_order])
return_processor = Agent(name="Return Processor", instructions="Process returns.", tools=[create_return])
payment_agent = Agent(name="Payment Agent", instructions="Handle payments.", tools=[process_payment])

# Level 2: Department managers
order_manager = Agent(
    name="Order Manager",
    instructions="Manage all order-related requests.",
    handoffs=[order_lookup_agent, return_processor],
)
billing_manager = Agent(
    name="Billing Manager",
    instructions="Manage all billing and payment requests.",
    handoffs=[payment_agent],
)

# Level 1: Front desk (entry point)
front_desk = Agent(
    name="Front Desk",
    instructions="Route customers to the right department.",
    handoffs=[order_manager, billing_manager],
)
```

---

## 13. ADVANCED PATTERNS

### Error Handling & Resilience

```python
from agents.exceptions import (
    MaxTurnsExceeded,
    ModelBehaviorError,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    AgentsException,
)

async def robust_run(agent, message, session=None):
    try:
        result = await Runner.run(
            agent, message,
            session=session,
            run_config=RunConfig(max_turns=20),
        )
        return result.final_output

    except InputGuardrailTripwireTriggered as e:
        return f"Input blocked: {e}"

    except OutputGuardrailTripwireTriggered as e:
        return f"Output blocked: {e}"

    except MaxTurnsExceeded:
        return "Task too complex. Please break it into smaller steps."

    except ModelBehaviorError as e:
        logger.error(f"Model misbehaved: {e}")
        return "An error occurred. Please try again."

    except AgentsException as e:
        logger.error(f"Agent error: {e}")
        raise
```

### Input Filtering / History Trimming

```python
from agents import RunConfig
from agents.run import CallModelData, ModelInputData

def trim_to_last_n_messages(n: int):
    def filter_fn(data: CallModelData[None]) -> ModelInputData:
        items = data.input.input
        # Keep system instructions + last N items
        trimmed = items[-n:] if len(items) > n else items
        return data.input.model_copy(update={"input": trimmed})
    return filter_fn

config = RunConfig(call_model_input_filter=trim_to_last_n_messages(10))
```

### Agent Visualization

```python
from agents.visualization import draw_graph

# Visualize agent network topology
draw_graph(triage_agent, filename="agent_graph")
# Generates agent_graph.png with nodes for each agent and edges for handoffs/tools
```

### Using Non-OpenAI Models (LiteLLM)

```python
from agents.extensions.models.litellm_model import LitellmModel

# Use any LiteLLM-supported model
agent = Agent(
    name="Claude Agent",
    instructions="Be helpful.",
    model=LitellmModel(model="anthropic/claude-3-5-sonnet-20241022"),
)

# Or via model string with litellm/ prefix
agent = Agent(
    name="Gemini Agent",
    model="litellm/google/gemini-pro",
)
```

---

## 14. PRODUCTION BEST PRACTICES

### Agent Design

- Write clear, specific system prompts. Vague instructions lead to unpredictable behavior.
- Use `handoff_description` on all agents to help triage routing.
- Prefer `output_type` with Pydantic models for structured, validated outputs.
- Use `model="gpt-4o-mini"` for guardrail agents to save cost.
- Set `max_turns` in `RunConfig` to prevent infinite loops.
- Use `AgentHooks` for logging, metrics, and side effects.

### Tool Design

- Write descriptive docstrings — they become the tool description the LLM sees.
- Use Pydantic models for complex tool inputs to get validation.
- Return structured data (dict/Pydantic) rather than plain strings where possible.
- Handle errors gracefully in tools and return informative error messages.
- Use context injection for DB connections, auth tokens, and shared state.

### Multi-Agent Architecture

- **Orchestrator pattern** (agents-as-tools): better for structured, sequential workflows where output flows through stages.
- **Handoff pattern** (decentralized): better for routing/triage where one agent fully takes over.
- Keep agents focused on a single domain (single responsibility principle).
- Use `SessionConfig` or sessions to maintain conversation state across turns.

### Session Management

- Use `SQLiteSession` for development, `RedisSession` for production.
- Pass `group_id` to `trace()` to link all traces from the same conversation.
- Never combine SDK sessions with server-side `conversation_id` in the same run.

### Guardrails Strategy

- Use `run_in_parallel=False` when input validation is cheap and you want to save tokens.
- Use `run_in_parallel=True` (default) for low-latency requirements.
- Place input guardrails on the first agent in a chain.
- Place output guardrails on the last agent in a chain.
- Guard expensive models with cheap classifier guardrails.

### Tracing & Debugging

- Always set `workflow_name` in `RunConfig` for clear trace labels.
- Use `group_id` to correlate traces from the same user session.
- Set `trace_include_sensitive_data=False` for PII compliance.
- Use `add_trace_processor()` to send traces to external systems (Logfire, Langfuse, etc.).

### Security

- Always validate and sanitize tool outputs before using them as agent input.
- Use tool guardrails for dangerous operations (SQL, file writes, API calls).
- Use `InputGuardrail` to prevent prompt injection and jailbreaks.
- Set `run_in_parallel=False` for security-critical guardrails.

### Performance

- Use `asyncio.gather()` to run independent agents in parallel.
- Use `gpt-4o-mini` or other cheap models for classification/routing tasks.
- Implement input filtering via `call_model_input_filter` to trim long histories.
- Cache tool results when appropriate using context object.

---

## 15. QUICK REFERENCE CHEAT SHEET

```python
# === SETUP ===
from agents import Agent, Runner, RunConfig
from agents import function_tool, handoff
from agents import InputGuardrail, OutputGuardrail, GuardrailFunctionOutput
from agents import SQLiteSession
from agents.tracing import trace

# === CREATE AGENT ===
agent = Agent(name="...", instructions="...", tools=[...], handoffs=[...])

# === RUN ===
result = Runner.run_sync(agent, "input")           # sync
result = await Runner.run(agent, "input")           # async
async with Runner.run_streamed(agent, "input") as s: ...  # streaming

# === RESULT ===
result.final_output                    # str output
result.final_output_as(MyModel)       # typed output
result.to_input_list()                # for manual multi-turn

# === TOOL ===
@function_tool
def my_tool(param: str) -> str: ...

# === HANDOFF ===
agent = Agent(handoffs=[other_agent])
agent = Agent(handoffs=[handoff(other_agent, on_handoff=callback)])

# === GUARDRAIL ===
async def check(ctx, agent, input_data) -> GuardrailFunctionOutput: ...
Agent(input_guardrails=[InputGuardrail(guardrail_function=check)])

# === SESSION ===
session = SQLiteSession("session_id")
result = await Runner.run(agent, "msg", session=session)

# === TRACING ===
with trace("My Workflow", group_id="session_123"): ...

# === CONTEXT ===
@dataclass
class Ctx: user_id: str
Agent[Ctx](instructions=lambda ctx, agent: f"User: {ctx.context.user_id}")

# === STRUCTURED OUTPUT ===
class Output(BaseModel): field: str
Agent(output_type=Output)
result.final_output_as(Output)

# === CLONE ===
agent.clone(name="New Name", instructions="New instructions")

# === AGENT AS TOOL ===
agent.as_tool("tool_name", "tool_description")
```

---

## Common Pitfalls to Avoid

1. **Missing `await`** — `Runner.run()` is async; use `Runner.run_sync()` for sync contexts.
2. **Context not passed through** — context must be passed to `Runner.run(..., context=ctx)`, not baked into agent.
3. **Circular handoffs** — agents can hand off to each other infinitely; set `max_turns`.
4. **Not setting `handoff_description`** — triage agents need these to route correctly.
5. **Using sessions with `conversation_id`** — these are mutually exclusive; pick one.
6. **Guardrails on non-first/last agents** — input guardrails only run on first agent; output guardrails only on last.
7. **Blocking event loop** — avoid `time.sleep()` in async tools; use `asyncio.sleep()`.
8. **Forgetting `output_type` validation** — `result.final_output_as(Model)` will raise if output doesn't match.
9. **Large tool outputs** — LLMs have context limits; trim large tool responses before returning.
10. **Not handling `MaxTurnsExceeded`** — always set `max_turns` and catch this exception in production.
