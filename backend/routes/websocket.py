"""WebSocket routes for real-time voice communication."""

import base64
import time
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect
from backend.services.voice_service import VoiceService
from backend.logging_config import get_logger

logger = get_logger(__name__)

# Global voice service instance (will be initialized in main.py)
voice_service: Optional[VoiceService] = None


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept WebSocket connection."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info("Client connected: %s", client_id)

    def disconnect(self, client_id: str):
        """Remove WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info("Client disconnected: %s", client_id)

    async def send_message(self, client_id: str, message: dict):
        """Send message to specific client."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                logger.exception("Error sending message to %s: %s", client_id, e)
                self.disconnect(client_id)


manager = ConnectionManager()


async def _send_error_and_idle(websocket: WebSocket, message: str) -> None:
    """Send error and idle state to client; ignore send failures (connection may be closed)."""
    try:
        await websocket.send_json({"type": "error", "data": message})
        await websocket.send_json({"type": "state", "data": "idle"})
    except Exception:
        pass


async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for voice communication.
    Errors (disconnect, MemoryError, etc.) are logged and close only this connection;
    the server stays alive and keeps accepting new connections.
    """
    client_id = None
    audio_buffer = []

    try:
        # Accept WebSocket connection FIRST (required by FastAPI)
        await websocket.accept()

        # Generate client ID
        client_id = f"client_{id(websocket)}"

        # Register connection immediately
        manager.active_connections[client_id] = websocket
        logger.info("Client connected: %s", client_id)

        # Send connection confirmation
        await websocket.send_json({"type": "state", "data": "connected"})

        if not voice_service:
            await websocket.send_json({
                "type": "error",
                "data": "Voice service not initialized",
            })
            return

        # Main message loop: on any error we log, notify client if possible, then exit loop
        while True:
            try:
                message = await websocket.receive_json()
                msg_type = message.get("type")

                # Handle connect message (optional, sent by client)
                if msg_type == "connect":
                    # Update client_id if provided
                    provided_id = message.get("client_id")
                    if provided_id and provided_id != client_id:
                        # Update client_id mapping
                        if client_id in manager.active_connections:
                            del manager.active_connections[client_id]
                        client_id = provided_id
                        manager.active_connections[client_id] = websocket
                    await websocket.send_json({"type": "state", "data": "connected"})
                    continue

                if msg_type == "start_recording":
                    audio_buffer = []
                    await websocket.send_json({"type": "state", "data": "listening"})

                elif msg_type == "audio_chunk":
                    # Receive audio chunk (base64 encoded)
                    audio_data_b64 = message.get("data", "")
                    try:
                        audio_chunk = base64.b64decode(audio_data_b64)
                        audio_buffer.append(audio_chunk)
                    except Exception as e:
                        logger.warning("Error decoding audio from %s: %s", client_id, e)

                elif msg_type == "stop_recording":
                    # Process complete audio
                    # Check if there's audio data in the message or buffer
                    final_chunk = message.get("data", "")
                    if final_chunk:
                        try:
                            audio_chunk = base64.b64decode(final_chunk)
                            audio_buffer.append(audio_chunk)
                        except Exception:
                            pass

                    if not audio_buffer:
                        await websocket.send_json({
                            "type": "error",
                            "data": "No audio data received",
                        })
                        continue

                    await websocket.send_json({"type": "state", "data": "processing"})

                    # Combine audio chunks
                    complete_audio = b"".join(audio_buffer)
                    audio_buffer = []

                    try:
                        # Record start time for processing
                        processing_start_time = time.time()

                        # Process audio through voice agent
                        transcribed_text, audio_response_iter = (
                            await voice_service.process_audio_chunk(complete_audio)
                        )

                        # Send transcription
                        await websocket.send_json({
                            "type": "transcription",
                            "data": transcribed_text,
                        })

                        # Calculate processing time (from start to speaking)
                        processing_time = time.time() - processing_start_time

                        # Stream audio response with processing time
                        await websocket.send_json({
                            "type": "state",
                            "data": "speaking",
                            "processing_time": round(processing_time, 3)
                        })

                        async for audio_chunk in audio_response_iter:
                            audio_b64 = base64.b64encode(
                                audio_chunk).decode("utf-8")
                            await websocket.send_json({
                                "type": "audio_chunk",
                                "data": audio_b64,
                            })

                        # Send completion
                        await websocket.send_json({"type": "state", "data": "idle"})

                    except Exception as e:
                        logger.exception("Error processing audio for %s: %s", client_id, e)
                        await _send_error_and_idle(websocket, f"Processing error: {str(e)}")

                elif msg_type == "text_message":
                    # Process text message
                    text = message.get("data", "")
                    if not text:
                        await manager.send_message(
                            client_id,
                            {
                                "type": "error",
                                "data": "Empty text message",
                            },
                        )
                        continue

                    await websocket.send_json({"type": "state", "data": "processing"})

                    try:
                        # Record start time for processing
                        processing_start_time = time.time()

                        response_text, audio_response_iter = (
                            await voice_service.process_text_message(text)
                        )

                        # Send text response
                        await websocket.send_json({
                            "type": "transcription",
                            "data": response_text,
                        })

                        # Calculate processing time (from start to speaking)
                        processing_time = time.time() - processing_start_time

                        # Stream audio response with processing time
                        await websocket.send_json({
                            "type": "state",
                            "data": "speaking",
                            "processing_time": round(processing_time, 3)
                        })

                        audio_chunk_count = 0
                        async for audio_chunk in audio_response_iter:
                            audio_chunk_count += 1
                            audio_b64 = base64.b64encode(
                                audio_chunk).decode("utf-8")
                            await websocket.send_json({
                                "type": "audio_chunk",
                                "data": audio_b64,
                            })

                        logger.debug("Sent %s audio chunks to %s", audio_chunk_count, client_id)
                        await websocket.send_json({"type": "state", "data": "idle"})

                    except Exception as e:
                        logger.exception("Error processing text for %s: %s", client_id, e)
                        await _send_error_and_idle(websocket, f"Processing error: {str(e)}")

                else:
                    await websocket.send_json({
                        "type": "error",
                        "data": f"Unknown message type: {msg_type}",
                    })

            except WebSocketDisconnect:
                logger.info("Client %s disconnected", client_id)
                break
            except Exception as e:
                # Log with full traceback (e.g. MemoryError, OSError) and exit loop
                # so this connection closes cleanly and server stays alive
                logger.exception(
                    "Error in WebSocket message loop for %s: %s",
                    client_id,
                    e,
                )
                await _send_error_and_idle(websocket, f"Server error: {str(e)}")
                break

    except WebSocketDisconnect:
        logger.info("Client %s disconnected", client_id or "unknown")
    except Exception as e:
        # Catch-all so no exception kills the server (e.g. MemoryError, OSError)
        logger.exception("WebSocket endpoint error for %s: %s", client_id, e)
        try:
            await _send_error_and_idle(websocket, f"Connection error: {str(e)}")
        except Exception:
            pass
    finally:
        if client_id:
            manager.disconnect(client_id)
