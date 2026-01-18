"""WebSocket routes for real-time voice communication."""

import json
import base64
import asyncio
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from backend.services.voice_service import VoiceService
from rich.console import Console

console = Console()

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
        console.print(f"[green]✓ Client connected: {client_id}[/green]")

    def disconnect(self, client_id: str):
        """Remove WebSocket connection."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            console.print(f"[yellow]✗ Client disconnected: {client_id}[/yellow]")

    async def send_message(self, client_id: str, message: dict):
        """Send message to specific client."""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                console.print(f"[red]Error sending message to {client_id}: {e}[/red]")
                self.disconnect(client_id)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for voice communication.

    Message format:
    - Client → Server:
      {
        "type": "audio_chunk" | "text_message" | "start_recording" | "stop_recording",
        "data": base64_encoded_audio | text_string,
        "client_id": "unique_client_id"
      }
    - Server → Client:
      {
        "type": "state" | "transcription" | "audio_chunk" | "error",
        "data": state_string | text | base64_audio | error_message
      }
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
        console.print(f"[green]✓ Client connected: {client_id}[/green]")
        
        # Send connection confirmation
        await websocket.send_json({"type": "state", "data": "connected"})
        
        # Try to get client_id from initial message if sent (non-blocking)
        # This is optional - if client sends a connect message, we'll handle it in the main loop

        if not voice_service:
            await websocket.send_json({
                "type": "error",
                "data": "Voice service not initialized",
            })
            return

        # Main message loop
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
                        console.print(f"[yellow]Error decoding audio: {e}[/yellow]")

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
                        # Process audio through voice agent
                        transcribed_text, audio_response_iter = (
                            await voice_service.process_audio_chunk(complete_audio)
                        )

                        # Send transcription
                        await websocket.send_json({
                            "type": "transcription",
                            "data": transcribed_text,
                        })

                        # Stream audio response
                        await websocket.send_json({"type": "state", "data": "speaking"})

                        async for audio_chunk in audio_response_iter:
                            audio_b64 = base64.b64encode(audio_chunk).decode("utf-8")
                            await websocket.send_json({
                                "type": "audio_chunk",
                                "data": audio_b64,
                            })

                        # Send completion
                        await websocket.send_json({"type": "state", "data": "idle"})

                    except Exception as e:
                        console.print(f"[red]Error processing audio: {e}[/red]")
                        await websocket.send_json({
                            "type": "error",
                            "data": f"Processing error: {str(e)}",
                        })
                        await websocket.send_json({"type": "state", "data": "idle"})

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
                        response_text, audio_response_iter = (
                            await voice_service.process_text_message(text)
                        )

                        # Send text response
                        await websocket.send_json({
                            "type": "transcription",
                            "data": response_text,
                        })

                        # Stream audio response
                        await websocket.send_json({"type": "state", "data": "speaking"})
                        console.print("[cyan]🔊 Sending 'speaking' state to client[/cyan]")

                        audio_chunk_count = 0
                        async for audio_chunk in audio_response_iter:
                            audio_chunk_count += 1
                            audio_b64 = base64.b64encode(audio_chunk).decode("utf-8")
                            console.print(f"[cyan]📤 Sending audio chunk {audio_chunk_count}: {len(audio_b64)} bytes (base64)[/cyan]")
                            await websocket.send_json({
                                "type": "audio_chunk",
                                "data": audio_b64,
                            })

                        console.print(f"[green]✅ Sent {audio_chunk_count} audio chunks total[/green]")
                        await websocket.send_json({"type": "state", "data": "idle"})

                    except Exception as e:
                        console.print(f"[red]Error processing text: {e}[/red]")
                        await websocket.send_json({
                            "type": "error",
                            "data": f"Processing error: {str(e)}",
                        })
                        await websocket.send_json({"type": "state", "data": "idle"})

                else:
                    await websocket.send_json({
                        "type": "error",
                        "data": f"Unknown message type: {msg_type}",
                    })

            except WebSocketDisconnect:
                break
            except Exception as e:
                console.print(f"[red]Error in message loop: {e}[/red]")
                try:
                    await websocket.send_json({
                        "type": "error",
                        "data": f"Server error: {str(e)}",
                    })
                except:
                    pass  # Connection might be closed

    except WebSocketDisconnect:
        console.print(f"[yellow]Client {client_id} disconnected[/yellow]")
    except Exception as e:
        console.print(f"[red]WebSocket error: {e}[/red]")
    finally:
        if client_id:
            manager.disconnect(client_id)

