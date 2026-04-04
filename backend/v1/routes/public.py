"""Public runtime routes for anonymous consumers (chat + voice).

Uses the agentic form engine (OpenAI Agents SDK) for conversation.
"""

from __future__ import annotations

import base64
import json
import logging

import numpy as np

from fastapi import APIRouter, Depends, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db, SessionLocal
from ..deps import extract_public_session_token
from ..models import Form, Message, RespondentSession, Submission
from ..schemas import (
    CompleteSessionResponse,
    MessageItem,
    MessagesListResponse,
    PublicMessageRequest,
    PublicMessageResponse,
    PublicSessionCreateRequest,
    PublicSessionCreateResponse,
)
from ..security import create_public_session_token, decode_token
from ..services.agent_engine import generate_initial_greeting, process_agent_message, stream_agent_message
from ..services.voice_workflow import FormAgentVoiceWorkflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public", tags=["v1-public"])


# ---------------------------------------------------------------------------
# Create session
# ---------------------------------------------------------------------------

@router.post("/f/{slug}/sessions", response_model=PublicSessionCreateResponse)
async def create_public_session(
    slug: str,
    payload: PublicSessionCreateRequest,
    db: Session = Depends(get_db),
):
    """Create a new consumer session for an agentic form."""
    form = db.execute(
        select(Form).where(Form.slug == slug, Form.status == "published")
    ).scalar_one_or_none()

    if not form:
        raise HTTPException(status_code=404, detail="Form is not available")

    # Validate form has agentic configuration
    if not form.system_prompt and not form.fields_schema:
        raise HTTPException(status_code=400, detail="Form is not configured")

    respondent_session = RespondentSession(
        form_id=form.id,
        form_version_id=None,  # Agentic forms don't use form versions
        channel=payload.channel,
        locale=payload.locale,
        status="active",
        current_node_id=None,  # No graph nodes in agentic mode
        metadata_json=payload.metadata,
    )
    db.add(respondent_session)
    db.flush()

    token = create_public_session_token(respondent_session.id)

    # Generate initial greeting via the agent
    greeting = await generate_initial_greeting(db, respondent_session)
    db.commit()

    return PublicSessionCreateResponse(
        session_id=respondent_session.id,
        session_token=token,
        state="active",
        assistant_message=greeting,
    )


# ---------------------------------------------------------------------------
# Send message (chat)
# ---------------------------------------------------------------------------

@router.post("/sessions/{session_id}/message", response_model=PublicMessageResponse)
async def public_message(
    session_id: str,
    payload: PublicMessageRequest,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Process a user message through the agentic form engine."""
    token = extract_public_session_token(authorization)
    claims = decode_token(token)
    if claims.get("type") != "public_session" or claims.get("sid") != session_id:
        raise HTTPException(status_code=401, detail="Invalid session token")

    respondent_session = db.get(RespondentSession, session_id)
    if not respondent_session:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await process_agent_message(db, respondent_session, payload.message)
    db.commit()

    return PublicMessageResponse(
        session_id=session_id,
        state=result.state,
        accepted=result.accepted,
        assistant_message=result.assistant_message,
    )


# ---------------------------------------------------------------------------
# Send message (chat) — streaming SSE
# ---------------------------------------------------------------------------

@router.post("/sessions/{session_id}/message/stream")
async def public_message_stream(
    session_id: str,
    payload: PublicMessageRequest,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Stream the agent's response token-by-token via SSE."""
    token = extract_public_session_token(authorization)
    claims = decode_token(token)
    if claims.get("type") != "public_session" or claims.get("sid") != session_id:
        raise HTTPException(status_code=401, detail="Invalid session token")

    respondent_session = db.get(RespondentSession, session_id)
    if not respondent_session:
        raise HTTPException(status_code=404, detail="Session not found")

    async def event_generator():
        try:
            async for event_type, data in stream_agent_message(db, respondent_session, payload.message):
                yield f"data: {json.dumps({'type': event_type, **data})}\n\n"
        except Exception as exc:
            logger.exception("SSE stream error: %s", exc)
            yield f"data: {json.dumps({'type': 'error', 'content': 'Stream failed'})}\n\n"
        finally:
            db.commit()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Get messages (for reconnect/resume)
# ---------------------------------------------------------------------------

@router.get("/sessions/{session_id}/messages", response_model=MessagesListResponse)
def list_session_messages(
    session_id: str,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    """Get chat history for a session."""
    token = extract_public_session_token(authorization)
    claims = decode_token(token)
    if claims.get("type") != "public_session" or claims.get("sid") != session_id:
        raise HTTPException(status_code=401, detail="Invalid session token")

    respondent_session = db.get(RespondentSession, session_id)
    if not respondent_session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    ).scalars().all()

    return MessagesListResponse(
        session_id=session_id,
        messages=[
            MessageItem(
                id=m.id,
                role=m.role,
                content=m.content,
                created_at=m.created_at.isoformat(),
            )
            for m in messages
        ],
    )


# ---------------------------------------------------------------------------
# Complete session manually
# ---------------------------------------------------------------------------

@router.post("/sessions/{session_id}/complete", response_model=CompleteSessionResponse)
def complete_session(
    session_id: str,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    token = extract_public_session_token(authorization)
    claims = decode_token(token)
    if claims.get("type") != "public_session" or claims.get("sid") != session_id:
        raise HTTPException(status_code=401, detail="Invalid session token")

    respondent_session = db.get(RespondentSession, session_id)
    if not respondent_session:
        raise HTTPException(status_code=404, detail="Session not found")

    respondent_session.status = "completed"
    respondent_session.current_node_id = None

    submission = db.execute(
        select(Submission).where(Submission.session_id == session_id)
    ).scalar_one_or_none()
    if not submission:
        submission = Submission(form_id=respondent_session.form_id, session_id=session_id, status="completed")
        db.add(submission)
        db.flush()

    db.commit()

    return CompleteSessionResponse(session_id=session_id, status="completed", submission_id=submission.id)


# ---------------------------------------------------------------------------
# Voice WebSocket
# ---------------------------------------------------------------------------

@router.websocket("/sessions/{session_id}/voice")
async def public_voice_session(websocket: WebSocket, session_id: str):
    """Voice websocket for session-bound runtime using the agent engine.

    Protocol:
    - client sends JSON {type:"auth", token:"..."}
    - client streams {type:"audio_chunk", data:"base64"} and then {type:"stop"}
    - server responds with transcription + assistant_message + audio
    """

    await websocket.accept()
    db = SessionLocal()
    audio_chunks: list[bytes] = []
    authed = False

    try:
        voice_service = websocket.app.state.voice_service if hasattr(websocket.app.state, "voice_service") else None

        while True:
            payload = await websocket.receive_json()
            msg_type = payload.get("type")

            if msg_type == "auth":
                token = payload.get("token", "")
                claims = decode_token(token)
                if claims.get("type") != "public_session" or claims.get("sid") != session_id:
                    await websocket.send_json({"type": "error", "data": "Invalid session token"})
                    await websocket.close(code=4401)
                    return
                authed = True

                # Send initial prompt via agent engine
                respondent_session = db.get(RespondentSession, session_id)
                if respondent_session and respondent_session.status == "active":
                    # Check if greeting already exists (from session creation)
                    existing_msgs = db.execute(
                        select(Message).where(Message.session_id == session_id)
                    ).scalars().all()

                    if existing_msgs:
                        # Use the last assistant message as the greeting
                        last_assistant = [m for m in existing_msgs if m.role == "assistant"]
                        prompt = last_assistant[-1].content if last_assistant else "Welcome! Let's get started."
                    else:
                        prompt = await generate_initial_greeting(db, respondent_session)
                        db.commit()

                    await websocket.send_json({"type": "state", "data": "connected"})
                    await websocket.send_json({
                        "type": "assistant_message",
                        "data": prompt,
                        "state": "active",
                    })

                    # Synthesize greeting as audio (TTS only — do not run through voice agent LLM)
                    if voice_service:
                        try:
                            async for pcm_chunk in voice_service.synthesize_speech(prompt):
                                encoded = base64.b64encode(pcm_chunk).decode("ascii")
                                await websocket.send_json({"type": "audio_chunk", "data": encoded})
                        except Exception as tts_err:
                            logger.exception("Greeting TTS failed: %s", tts_err)
                        finally:
                            await websocket.send_json({"type": "audio_end"})
                    else:
                        await websocket.send_json({"type": "audio_end"})

                else:
                    await websocket.send_json({"type": "state", "data": "connected"})
                    await websocket.send_json({"type": "audio_end"})
                continue

            if not authed:
                await websocket.send_json({"type": "error", "data": "Authenticate first"})
                continue

            if msg_type == "start_recording":
                # Clear any orphaned chunks from a prior turn (belt-and-suspenders with client timing).
                audio_chunks = []
                continue

            if msg_type == "audio_chunk":
                try:
                    audio_chunks.append(base64.b64decode(payload.get("data", "")))
                except Exception:
                    await websocket.send_json({"type": "error", "data": "Invalid audio chunk"})
                continue

            if msg_type == "stop":
                transcript_override = (payload.get("transcript") or "").strip()
                respondent_session = db.get(RespondentSession, session_id)
                if not respondent_session:
                    await websocket.send_json({"type": "error", "data": "Session not found"})
                    await websocket.close(code=4404)
                    return

                combined_audio = b"".join(audio_chunks)
                audio_chunks = []

                # Text-only turn (optional client hint): skip STT pipeline
                if not combined_audio and transcript_override and voice_service:
                    try:
                        result = await process_agent_message(
                            db, respondent_session, transcript_override
                        )
                        db.commit()
                        await websocket.send_json(
                            {"type": "transcription", "data": transcript_override}
                        )
                        await websocket.send_json(
                            {
                                "type": "assistant_message",
                                "data": result.assistant_message,
                                "state": result.state,
                                "accepted": result.accepted,
                            }
                        )
                        try:
                            async for pcm_chunk in voice_service.synthesize_speech(
                                result.assistant_message
                            ):
                                enc = base64.b64encode(pcm_chunk).decode("ascii")
                                await websocket.send_json({"type": "audio_chunk", "data": enc})
                        except Exception as tts_err:
                            logger.exception("Text-turn TTS failed: %s", tts_err)
                        finally:
                            await websocket.send_json({"type": "audio_end"})
                    except Exception as e:
                        logger.exception("Voice text turn failed: %s", e)
                        await websocket.send_json(
                            {"type": "error", "data": f"Processing error: {e}"}
                        )
                    continue

                if not combined_audio:
                    await websocket.send_json(
                        {"type": "error", "data": "No audio data received"}
                    )
                    continue

                if not voice_service:
                    await websocket.send_json(
                        {"type": "error", "data": "Voice service not initialized"}
                    )
                    continue

                try:
                    audio_array = voice_service.audio_bytes_to_int16_24k(combined_audio)
                except Exception as dec_err:
                    logger.warning("Audio decode failed: %s", dec_err)
                    await websocket.send_json(
                        {
                            "type": "error",
                            "data": f"Audio decode failed: {dec_err}",
                        }
                    )
                    continue

                # Reject near-silent audio to prevent Whisper hallucinations
                rms = float(np.sqrt(np.mean(audio_array.astype(np.float64) ** 2)))
                duration_s = len(audio_array) / 24000.0
                logger.debug(
                    "Audio stats: rms=%.1f duration=%.2fs samples=%d",
                    rms, duration_s, len(audio_array),
                )
                if rms < 50 or duration_s < 0.3:
                    logger.warning(
                        "Audio too quiet or too short (rms=%.1f, dur=%.2fs) — skipping STT",
                        rms, duration_s,
                    )
                    await websocket.send_json(
                        {
                            "type": "assistant_message",
                            "data": "I didn't quite catch that. Could you please speak a bit louder?",
                            "state": respondent_session.status,
                            "accepted": True,
                        }
                    )
                    await websocket.send_json({"type": "audio_end"})
                    continue

                from agents.voice import AudioInput

                workflow = FormAgentVoiceWorkflow(
                    SessionLocal,
                    session_id,
                    respondent_session.form_id,
                )
                pipeline = voice_service.create_voice_pipeline(workflow)

                try:
                    vp_result = await pipeline.run(AudioInput(buffer=audio_array))
                except Exception as pipe_err:
                    logger.exception("VoicePipeline failed: %s", pipe_err)
                    await websocket.send_json(
                        {"type": "error", "data": f"Voice processing failed: {pipe_err}"}
                    )
                    await websocket.send_json(
                        {
                            "type": "assistant_message",
                            "data": "",
                            "state": respondent_session.status,
                            "accepted": False,
                        }
                    )
                    await websocket.send_json({"type": "audio_end"})
                    continue

                audio_parts: list[bytes] = []
                stream_exc: Exception | None = None
                try:
                    async for event in vp_result.stream():
                        et = getattr(event, "type", "")
                        if et == "voice_stream_event_lifecycle":
                            ev = getattr(event, "event", "")
                            logger.debug(
                                "VoicePipeline lifecycle: %s session=%s",
                                ev,
                                session_id,
                            )
                        elif et == "voice_stream_event_audio":
                            data = getattr(event, "data", None)
                            if data is not None:
                                if isinstance(data, np.ndarray):
                                    audio_parts.append(data.tobytes())
                                elif isinstance(data, (bytes, bytearray)):
                                    audio_parts.append(bytes(data))
                        elif et == "voice_stream_event_error":
                            err = getattr(event, "error", None)
                            logger.error(
                                "VoicePipeline emitted VoiceStreamEventError: %s",
                                err,
                                exc_info=err if isinstance(err, BaseException) else None,
                            )
                except Exception as stream_err:
                    stream_exc = stream_err
                    logger.exception("Voice pipeline stream failed: %s", stream_err)
                finally:
                    pcm_out = b"".join(audio_parts) if audio_parts else None
                    if pcm_out:
                        chunk_size = 4096
                        for i in range(0, len(pcm_out), chunk_size):
                            enc = base64.b64encode(pcm_out[i : i + chunk_size]).decode("ascii")
                            await websocket.send_json({"type": "audio_chunk", "data": enc})

                    lr = workflow.last_result or {}
                    # SDK VoicePipeline does not emit STT as a stream event; use workflow result.
                    if lr.get("transcription"):
                        await websocket.send_json(
                            {"type": "transcription", "data": lr["transcription"]}
                        )

                    await websocket.send_json(
                        {
                            "type": "assistant_message",
                            "data": lr.get("response", ""),
                            "state": lr.get("state", respondent_session.status),
                            "accepted": lr.get("accepted", True),
                        }
                    )
                    if stream_exc is not None:
                        await websocket.send_json(
                            {
                                "type": "error",
                                "data": f"Voice stream interrupted: {stream_exc}",
                            }
                        )
                    await websocket.send_json({"type": "audio_end"})
                continue

            await websocket.send_json({"type": "error", "data": f"Unknown message type: {msg_type}"})

    except WebSocketDisconnect:
        return
    finally:
        db.close()
