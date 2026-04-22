"""Agentic Forms engine using OpenAI Agents SDK with function calling.

Uses Groq Llama via LiteLLM for natural conversation and the save_answer tool
to persist form data. Requires GROQ_API_KEY.
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
from agents.stream_events import RawResponsesStreamEvent
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Answer, Form, Message, RespondentSession, Submission

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
set_tracing_disabled(True)

logger = logging.getLogger(__name__)

MODEL = "groq/llama-3.3-70b-versatile"


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
    #: At most one successful save_answer per Runner / voice workflow run.
    save_answer_called: bool = False


# ---------------------------------------------------------------------------
# Tool – answer validation
# ---------------------------------------------------------------------------

POLITE_FILLERS = frozenset({
    "thank you", "thanks", "thank you so much", "thanks a lot",
    "got it", "okay", "ok", "sure", "alright", "great", "perfect",
    "wonderful", "excellent", "nice", "good", "yes", "no", "yeah",
    "yep", "nope", "right", "cool", "sounds good", "that's great",
    "that's fine", "that sounds good", "hi", "hello", "hey", "bye",
    "goodbye", "go ahead", "please", "of course", "absolutely",
    "mm-hmm", "uh-huh", "you're welcome", "no problem",
})


def _is_invalid_answer_value(value: str) -> str | None:
    """Return an error string if *value* must not be persisted, else None."""
    if not value or not value.strip():
        return "Value is empty."
    v = value.strip()
    vl = v.lower()
    if "[user" in vl and "]" in vl:
        return "Do not save placeholder text like [user's ...]. Save the actual words the user said."
    normalised = vl.rstrip(".!?,;:")
    if normalised in POLITE_FILLERS:
        return (
            f"'{v}' is a polite filler, NOT the user's real answer. "
            "Do NOT save it. Re-ask the question and wait for their actual answer."
        )
    return None


# ---------------------------------------------------------------------------
# Tool – save_answer
# ---------------------------------------------------------------------------

@function_tool
def save_answer(
    ctx: RunContextWrapper[FormSessionContext],
    field_name: str,
    value: str,
) -> str:
    """Save the user's ACTUAL spoken answer for a form field.

    CRITICAL RULES — read before every call:
    - value MUST contain the exact words the USER said, never your own words.
    - Do NOT pass polite phrases like "Thank you", "Sure", "Okay", "Great" as the value.
    - If the user only said a polite filler without giving a real answer, do NOT call
      this tool at all. Instead acknowledge them politely and re-ask the question.

    Args:
        field_name: Exact field name from the form schema (e.g. dining_experience, food_quality_rating).
        value: The user's actual spoken answer (string; for booleans use 'true' or 'false').
    """
    fctx: FormSessionContext = ctx.context
    db = fctx.db
    session_obj = fctx.respondent_session
    form = fctx.form

    logger.debug("save_answer called: field=%s value=%r", field_name, value)

    if fctx.save_answer_called:
        return (
            "Error: Only one save_answer is allowed per user turn. "
            "Do not call save_answer again. Respond with the next question only."
        )

    valid_fields = {f["name"] for f in (form.fields_schema or [])}
    if valid_fields and field_name not in valid_fields:
        return f"Error: '{field_name}' is not a valid field. Valid: {', '.join(sorted(valid_fields))}"

    rejection = _is_invalid_answer_value(value)
    if rejection:
        logger.warning("save_answer REJECTED: field=%s value=%r reason=%s", field_name, value, rejection)
        return f"Error: {rejection}"

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
    fctx.save_answer_called = True

    logger.info("save_answer SAVED: field=%s value=%r", field_name, value.strip())

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

LOCALE_LABELS = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "pt": "Portuguese", "ar": "Arabic", "zh": "Chinese", "ja": "Japanese",
    "ko": "Korean", "hi": "Hindi", "ur": "Urdu", "it": "Italian",
    "nl": "Dutch", "ru": "Russian", "tr": "Turkish",
}


def _build_instructions(
    form: Form,
    collected_answers: dict[str, str] | None = None,
    voice_mode: bool = False,
) -> str:
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

    voice_note = ""
    if voice_mode:
        voice_note = """
## Voice mode — CRITICAL instructions
You are conducting a voice interview. The user speaks their answers aloud ONE AT A TIME.

STRICT RULES — follow these exactly, every single turn:

1. Each call to your run() handles EXACTLY ONE user utterance. You MUST call save_answer
   at most ONCE per run. Never call save_answer more than once in the same response.

2. After calling save_answer, you get one more turn to respond with a brief acknowledgment
   and ONLY the next unanswered question. That is all you do.

3. NEVER answer questions on behalf of the user. NEVER infer, guess, or extrapolate
   answers to questions you have not yet asked. Only save what the user literally said.

4. NEVER use conversation history to pre-fill or overwrite answers. Each utterance is
   independent. Save only what the CURRENT user message contains.

5. If the user's message is ONLY a polite filler (e.g. "Thank you", "Okay", "Sure",
   "Yeah") with NO answer content, do NOT call save_answer. Acknowledge briefly
   and re-ask the same question.

6. Extract the SUBSTANTIVE content from the user's words:
   - User says "My name is Hamza Adil" -> save_answer(field_name="full_name", value="Hamza Adil")
   - User says "I play on PC" -> save_answer(field_name="gaming_platform", value="PC")
   - User says "About monthly" -> save_answer(field_name="play_frequency", value="monthly")

7. NEVER pass your own words as the value. NEVER pass greetings or acknowledgments."""

    locale = getattr(form, "locale", "en") or "en"
    lang_name = LOCALE_LABELS.get(locale, "English")
    lang_instruction = ""
    if locale != "en":
        lang_instruction = f"\n## Language\nCONDUCT THE ENTIRE CONVERSATION IN {lang_name.upper()}. All your responses, questions, and acknowledgments MUST be in {lang_name}. The user may respond in {lang_name} or English; accept both.\n"

    # Conditional logic note
    conditions_note = ""
    has_conditions = any(f.get("conditions") for f in (form.fields_schema or []))
    if has_conditions:
        conditions_note = "\n## Conditional Fields\nSome fields have conditions. Only ask for a field if its conditions are met based on previously collected answers. Skip fields whose conditions are not satisfied.\n"

    return f"""You are a conversational form assistant. Persona: {persona}
{voice_note}
{lang_instruction}
## Form: {form.title}
{form.description or ""}

## Admin
{admin_prompt or "Collect all required fields."}

## Fields
{fields_desc or "No schema."}
{conditions_note}
{progress}
## Rules
1. Ask one question at a time. When the user answers, call save_answer ONCE with the field name and the user's ACTUAL words as the value, then respond briefly and ask the next unanswered question.
2. Only save answers the user explicitly gave. Do not guess, infer, or fill in answers from context or prior turns.
3. When save_answer says all required fields are collected, thank the user and say goodbye.
4. Keep replies short (1-2 sentences).
5. If the user says something like "Thank you" or "Okay" without answering the question, do NOT call save_answer. Simply acknowledge and re-ask the same question.
6. NEVER call save_answer more than once per response. NEVER pre-answer future questions."""


# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------

def _get_llm() -> LitellmModel:
    api_key = os.getenv("GROQ_API_KEY", "")
    return LitellmModel(model=MODEL, api_key=api_key)


def build_form_agent(
    form: Form,
    collected_answers: dict[str, str] | None = None,
    voice_mode: bool = False,
) -> Agent[FormSessionContext]:
    if not _supports_function_calling():
        logger.warning("Model %s does not support function calling; tool calls may fail.", MODEL)
    instructions = _build_instructions(form, collected_answers=collected_answers, voice_mode=voice_mode)
    return Agent(
        name=f"FormAgent-{form.slug}",
        instructions=instructions,
        model=_get_llm(),
        model_settings=ModelSettings(temperature=0.4, max_tokens=500, parallel_tool_calls=False),
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
    *,
    persist_messages: bool = True,
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
    voice_mode = getattr(respondent_session, "channel", None) == "voice"
    agent = build_form_agent(form, collected_answers=collected, voice_mode=voice_mode)
    context = FormSessionContext(
        db=db,
        respondent_session=respondent_session,
        form=form,
        collected_answers=collected,
    )

    if persist_messages:
        db.add(Message(session_id=respondent_session.id, role="user", content=user_text))
        db.flush()

    history = _load_history(db, respondent_session.id)
    input_items = history + [{"role": "user", "content": user_text}]

    import asyncio

    assistant_message = None
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

    if persist_messages:
        db.add(Message(session_id=respondent_session.id, role="assistant", content=assistant_message))
        db.flush()
    state = respondent_session.status

    return AgentResult(assistant_message=assistant_message, state=state, accepted=True)


async def stream_agent_message(
    db: Session,
    respondent_session: RespondentSession,
    user_text: str,
):
    """Yield (event_type, data) tuples as the agent streams its response.

    Event types: "delta" (token), "done" (final summary with state).
    """
    if respondent_session.status != "active":
        yield "done", {"state": respondent_session.status, "accepted": False, "assistant_message": "This session is no longer active."}
        return

    form = db.get(Form, respondent_session.form_id)
    if not form:
        yield "done", {"state": "error", "accepted": False, "assistant_message": "Form not found."}
        return

    collected = _load_collected_answers(db, respondent_session.id)
    voice_mode = getattr(respondent_session, "channel", None) == "voice"
    agent = build_form_agent(form, collected_answers=collected, voice_mode=voice_mode)
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

    streamed_text = ""
    final_output = ""
    try:
        result = Runner.run_streamed(
            starting_agent=agent,
            input=input_items,
            context=context,
            max_turns=5,
        )
        async for event in result.stream_events():
            if isinstance(event, RawResponsesStreamEvent):
                data = event.data
                event_type = getattr(data, "type", "")
                if event_type == "response.output_text.delta":
                    delta = getattr(data, "delta", "")
                    if delta:
                        streamed_text += delta
                        yield "delta", {"content": delta}

        final = await result.get_final_result()
        final_output = str(final.final_output).strip() if final.final_output else ""

        if not streamed_text and final_output:
            streamed_text = final_output
            yield "delta", {"content": final_output}

    except Exception as exc:
        logger.exception("Streaming agent run failed: %s", exc)
        if not streamed_text:
            streamed_text = "I'm having trouble processing that. Please try again."
            yield "delta", {"content": streamed_text}

    if not streamed_text:
        streamed_text = "Could you repeat that?"
        yield "delta", {"content": streamed_text}

    saved_message = final_output or streamed_text

    db.add(Message(session_id=respondent_session.id, role="assistant", content=saved_message))
    db.flush()

    db.expire(respondent_session)
    state = respondent_session.status

    yield "done", {"state": state, "accepted": True, "assistant_message": saved_message}


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
        tools=[],
    )

    import asyncio

    greeting = None
    for attempt in range(3):
        try:
            result = await Runner.run(
                starting_agent=greeting_agent,
                input="Generate a short, friendly greeting for someone starting this form. Mention what you'll ask about. 2-3 sentences. No tools.",
                max_turns=1,
            )
            greeting = str(result.final_output).strip() if result.final_output else None
            if greeting:
                break
        except Exception as exc:
            logger.warning("Greeting attempt %d failed: %s", attempt + 1, exc)
            await asyncio.sleep(0.5 * (attempt + 1))

    if not greeting:
        greeting = f"Hi! Welcome to {form.title}. I'll ask you a few questions - let's get started!"

    db.add(Message(session_id=respondent_session.id, role="assistant", content=greeting))
    db.flush()
    return greeting
