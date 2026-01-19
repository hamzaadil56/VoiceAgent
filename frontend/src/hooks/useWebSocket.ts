import { useEffect, useRef, useState, useCallback } from "react";

export type AgentState =
	| "idle"
	| "listening"
	| "processing"
	| "speaking"
	| "connected"
	| "disconnected";

interface WebSocketMessage {
	type: "state" | "transcription" | "audio_chunk" | "error";
	data: string;
	processing_time?: number;
}

interface UseWebSocketReturn {
	connect: () => void;
	disconnect: () => void;
	sendMessage: (type: string, data: string) => void;
	state: AgentState;
	transcription: string;
	error: string | null;
	isConnected: boolean;
	processingTime: number | null;
}

export function useWebSocket(
	onAudioChunk?: (base64Audio: string) => void,
	onTranscription?: (text: string) => void
): UseWebSocketReturn {
	const [state, setState] = useState<AgentState>("disconnected");
	const [transcription, setTranscription] = useState<string>("");
	const [error, setError] = useState<string | null>(null);
	const [isConnected, setIsConnected] = useState(false);
	const [processingTime, setProcessingTime] = useState<number | null>(null);

	const wsRef = useRef<WebSocket | null>(null);
	const stateRef = useRef<AgentState>("disconnected");
	const clientIdRef = useRef<string>(
		`client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
	);

	// Keep state ref in sync
	useEffect(() => {
		stateRef.current = state;
	}, [state]);

	const connect = useCallback(() => {
		if (wsRef.current?.readyState === WebSocket.OPEN) {
			return;
		}

		try {
			const wsUrl =
				import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws";
			const ws = new WebSocket(wsUrl);

			ws.onopen = () => {
				console.log("WebSocket connected");
				setIsConnected(true);
				setState("connected");
				setError(null);

				// Send initial connection message (optional - backend accepts immediately)
				try {
					ws.send(
						JSON.stringify({
							type: "connect",
							client_id: clientIdRef.current,
						})
					);
				} catch (e) {
					console.warn("Could not send initial connect message:", e);
				}
			};

			ws.onmessage = (event) => {
				try {
					const message: WebSocketMessage = JSON.parse(event.data);
					console.log("📨 WebSocket message received:", {
						type: message.type,
						dataLength: message.data?.length,
						dataPreview: message.data?.substring(0, 100),
					});

					switch (message.type) {
						case "state":
							console.log("🔄 State change:", message.data);
							setState(message.data as AgentState);
							// Store processing time if provided (comes with 'speaking' state)
							if (message.processing_time !== undefined) {
								setProcessingTime(message.processing_time);
							}
							// Clear processing time when starting a new recording or when processing starts again
							if (
								message.data === "listening" ||
								message.data === "processing"
							) {
								setProcessingTime(null);
							}
							break;
						case "transcription":
							console.log("📝 Transcription:", message.data);
							setTranscription(message.data);
							if (onTranscription) {
								onTranscription(message.data);
							}
							break;
						case "audio_chunk":
							console.log(
								"🎵 Audio chunk received, length:",
								message.data?.length
							);
							if (onAudioChunk) {
								onAudioChunk(message.data);
							}
							break;
						case "error":
							setError(message.data);
							console.error("❌ WebSocket error:", message.data);
							break;
					}
				} catch (err) {
					console.error("Error parsing WebSocket message:", err);
				}
			};

			ws.onerror = (err) => {
				console.error("WebSocket error:", err);
				setError("WebSocket connection error");
				setState("disconnected");
				setIsConnected(false);
			};

			ws.onclose = () => {
				console.log("WebSocket disconnected");
				setState("disconnected");
				setIsConnected(false);
			};

			wsRef.current = ws;
		} catch (err) {
			console.error("Failed to connect WebSocket:", err);
			setError("Failed to connect to server");
			setState("disconnected");
			setIsConnected(false);
		}
	}, [onAudioChunk, onTranscription]);

	const disconnect = useCallback(() => {
		if (wsRef.current) {
			wsRef.current.close();
			wsRef.current = null;
		}
		setState("disconnected");
		setIsConnected(false);
	}, []);

	const sendMessage = useCallback((type: string, data: string) => {
		if (wsRef.current?.readyState === WebSocket.OPEN) {
			wsRef.current.send(
				JSON.stringify({
					type,
					data,
					client_id: clientIdRef.current,
				})
			);
		} else {
			console.warn("WebSocket is not connected");
		}
	}, []);

	useEffect(() => {
		return () => {
			disconnect();
		};
	}, [disconnect]);

	return {
		connect,
		disconnect,
		sendMessage,
		state,
		transcription,
		error,
		isConnected,
		processingTime,
	};
}
