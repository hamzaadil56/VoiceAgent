"""Agentic Forms engine using OpenAI Agents SDK with function calling.

Uses openai/gpt-4o-mini via OpenRouter for natural conversation
and the save_answer tool to persist form data. Requires OPEN_ROUTER_API_KEY.
"""

from __future__ import annotations

import logging
import os
import warnings
from dataclasses import dataclass, field
from typing import Any

from agents import Agent, ModelSettings, Runner, function_tool, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
from agents import RunContextWrapper
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Answer, Form, Message, RespondentSession, Submission

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
set_tracing_disabled(True)

# LiteLLM expects OPENROUTER_API_KEY; bridge from OPEN_ROUTER_API_KEY
if os.getenv("OPEN_ROUTER_API_KEY") and not os.getenv("OPENROUTER_API_KEY"):
    os.environ["OPENROUTER_API_KEY"] = os.getenv("OPEN_ROUTER_API_KEY", "")

logger = logging.getLogger(__name__)

MODEL = "openrouter/openai/gpt-4o-mini"


def _supports_function_calling() -> bool:
    try:
        return bool(__import__("litellm").supports_function_calling(MODEL))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------

@dataclass
class FormSessionContext:
    db: Session
    respondent_session: RespondentSession
    form: Form
    collected_answers: dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------

@function_tool
def save_answer(
    ctx: RunContextWrapper[FormSessionContext],
    field_name: str,
    value: str,
) -> str:
    """Save the user's answer for a form field. Call this when the user has provided an answer. After saving, ask for the next required field or thank them if all are collected.

    Args:
        field_name: Exact field name from the form schema (e.g. dining_experience, food_quality_rating).
        value: The value the user provided (string; for booleans use 'true' or 'false').
    """
    fctx: FormSessionContext = ctx.context
    db = fctx.db
    session_obj = fctx.respondent_session
    form = fctx.form

    valid_fields = {f["name"] for f in (form.fields_schema or [])}
    if valid_fields and field_name not in valid_fields:
        return f"Error: '{field_name}' is not a valid field. Valid: {', '.join(sorted(valid_fields))}"

    existing = db.execute(
        select(Answer).where(
            Answer.session_id == session_obj.id,
            Answer.field_key == field_name,
        )
    ).scalar_one_or_none()

    if existing:
        existing.value_text = value.strip()
    else:
        db.add(
            Answer(
                session_id=session_obj.id,
                form_id=form.id,
                field_key=field_name,
                value_text=value.strip(),
            )
        )
    db.flush()
    fctx.collected_answers[field_name] = value.strip()

    fields_schema = form.fields_schema or []
    required = [f["name"] for f in fields_schema if f.get("required", True)]
    missing_required = [f for f in required if f not in fctx.collected_answers]

    if not missing_required:
        session_obj.status = "completed"
        session_obj.current_node_id = None
        existing_sub = db.execute(select(Submission).where(Submission.session_id == session_obj.id)).scalar_one_or_none()
        if not existing_sub:
            db.add(Submission(form_id=form.id, session_id=session_obj.id, status="completed"))
        db.flush()
        return "All required fields collected. Thank the user warmly and say goodbye."

    return f"Saved. Still need: {', '.join(missing_required)}. Ask the user for the next one only."


# ---------------------------------------------------------------------------
# Instructions
# ---------------------------------------------------------------------------

def _build_instructions(form: Form, collected_answers: dict[str, str] | None = None) -> str:
    fields_desc = ""
    if form.fields_schema:
        for f in form.fields_schema:
            req = "required" if f.get("required", True) else "optional"
            desc = f.get("description", "")
            fields_desc += f"  - {f['name']} ({req})" + (f": {desc}" if desc else "") + "\n"

    admin_prompt = (form.system_prompt or "").strip()
    persona = (form.persona or "Friendly and professional").strip()

    progress = ""
    if collected_answers:
        lines = [f"  - {k}: {v}" for k, v in collected_answers.items()]
        required = [f["name"] for f in (form.fields_schema or []) if f.get("required", True)]
        still = [f for f in required if f not in collected_answers]
        progress = f"\n## Progress\nCollected:\n" + "\n".join(lines) + f"\nStill needed: {', '.join(still) or 'none'}.\n"

    return f"""You are a conversational form assistant. Persona: {persona}

## Form: {form.title}
{form.description or ""}

## Admin
{admin_prompt or "Collect all required fields."}

## Fields
{fields_desc or "No schema."}
{progress}
## Rules
1. Ask one question at a time. When the user answers, call save_answer with the field name and their value, then respond naturally and ask the next question.
2. Only save answers the user explicitly gave. Do not guess or infer.
3. When save_answer says all required fields are collected, thank the user and say goodbye.
4. Keep replies short (1–2 sentences)."""


# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------

def _get_llm() -> LitellmModel:
    api_key = os.getenv("OPEN_ROUTER_API_KEY", "") or os.getenv("OPENROUTER_API_KEY", "")
    return LitellmModel(model=MODEL, api_key=api_key)


def build_form_agent(form: Form, collected_answers: dict[str, str] | None = None) -> Agent[FormSessionContext]:
    if not _supports_function_calling():
        logger.warning("Model %s does not support function calling; tool calls may fail.", MODEL)
    instructions = _build_instructions(form, collected_answers=collected_answers)
    return Agent(
        name=f"FormAgent-{form.slug}",
        instructions=instructions,
        model=_get_llm(),
        model_settings=ModelSettings(temperature=0.7, max_tokens=500, parallel_tool_calls=False),
        tools=[save_answer],
    )


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

@dataclass
class AgentResult:
    assistant_message: str
    state: str
    accepted: bool = True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_collected_answers(db: Session, session_id: str) -> dict[str, str]:
    rows = db.execute(select(Answer).where(Answer.session_id == session_id)).scalars().all()
    return {a.field_key: a.value_text for a in rows}


def _load_history(db: Session, session_id: str, max_messages: int = 10) -> list[dict[str, Any]]:
    messages = (
        db.execute(select(Message).where(Message.session_id == session_id).order_by(Message.created_at.asc()))
        .scalars().all()
    )
    items = [{"role": m.role, "content": m.content} for m in messages if m.role in ("user", "assistant")]
    if len(items) > max_messages:
        items = items[-max_messages:]
    return items


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def process_agent_message(
    db: Session,
    respondent_session: RespondentSession,
    user_text: str,
) -> AgentResult:
    if respondent_session.status != "active":
        return AgentResult(
            assistant_message="This session is no longer active.",
            state=respondent_session.status,
            accepted=False,
        )

    form = db.get(Form, respondent_session.form_id)
    if not form:
        return AgentResult(assistant_message="Form not found.", state="error", accepted=False)

    collected = _load_collected_answers(db, respondent_session.id)
    agent = build_form_agent(form, collected_answers=collected)
    context = FormSessionContext(
        db=db,
        respondent_session=respondent_session,
        form=form,
        collected_answers=collected,
    )

    db.add(Message(session_id=respondent_session.id, role="user", content=user_text))
    db.flush()

    history = _load_history(db, respondent_session.id)
    input_items = history + [{"role": "user", "content": user_text}]

    import asyncio

    assistant_message = None
    last_error = None
    for attempt in range(3):
        try:
            result = await Runner.run(
                starting_agent=agent,
                input=input_items,
                context=context,
                max_turns=5,
            )
            assistant_message = str(result.final_output).strip() if result.final_output else "Could you repeat that?"
            break
        except Exception as exc:
            last_error = exc
            err = str(exc).lower()
            if any(x in err for x in ("tool_use_failed", "rate_limit", "429", "timeout")):
                logger.warning("Agent attempt %d failed (retrying): %s", attempt + 1, exc)
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
            logger.exception("Agent run failed: %s", exc)
            break

    if assistant_message is None:
        db.expire(respondent_session)
        if respondent_session.status == "completed":
            assistant_message = "Thank you! Your responses have been recorded."
        else:
            fresh = _load_collected_answers(db, respondent_session.id)
            required = [f["name"] for f in (form.fields_schema or []) if f.get("required", True)]
            missing = [f for f in required if f not in fresh]
            if not missing:
                respondent_session.status = "completed"
                existing_sub = db.execute(select(Submission).where(Submission.session_id == respondent_session.id)).scalar_one_or_none()
                if not existing_sub:
                    db.add(Submission(form_id=form.id, session_id=respondent_session.id, status="completed"))
                db.flush()
                assistant_message = "Thank you! Your responses have been recorded."
            elif len(fresh) > len(collected):
                next_f = missing[0]
                desc = next((f.get("description", next_f) for f in (form.fields_schema or []) if f["name"] == next_f), next_f)
                assistant_message = f"Got it. Could you tell me: {desc}?"
            else:
                assistant_message = "I'm having trouble processing that. Please try again."

    db.add(Message(session_id=respondent_session.id, role="assistant", content=assistant_message))
    db.flush()
    state = respondent_session.status

    return AgentResult(assistant_message=assistant_message, state=state, accepted=True)


async def generate_initial_greeting(db: Session, respondent_session: RespondentSession) -> str:
    form = db.get(Form, respondent_session.form_id)
    if not form:
        return "Welcome! Let's get started."

    instructions = _build_instructions(form)
    greeting_agent = Agent(
        name=f"Greeting-{form.slug}",
        instructions=instructions,
        model=_get_llm(),
        model_settings=ModelSettings(temperature=0.7, max_tokens=300),
        tools=[],  # no tools for greeting
    )

    import asyncio

    greeting = None
    for attempt in range(3):
        try:
            result = await Runner.run(
                starting_agent=greeting_agent,
                input="Generate a short, friendly greeting for someone starting this form. Mention what you'll ask about. 2–3 sentences. No tools.",
                max_turns=1,
            )
            greeting = str(result.final_output).strip() if result.final_output else None
            if greeting:
                break
        except Exception as exc:
            logger.warning("Greeting attempt %d failed: %s", attempt + 1, exc)
            await asyncio.sleep(0.5 * (attempt + 1))

    if not greeting:
        greeting = f"Hi! Welcome to {form.title}. I'll ask you a few questions—let's get started!"

    db.add(Message(session_id=respondent_session.id, role="assistant", content=greeting))
    db.flush()
    return greeting
