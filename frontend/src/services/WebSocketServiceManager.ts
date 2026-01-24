import { AgentState } from "../hooks/useWebSocket";

export interface WebSocketMessage {
	type: "state" | "transcription" | "audio_chunk" | "error";
	data: string;
	processing_time?: number;
}

export interface WebSocketServiceCallbacks {
	onStateChange?: (state: AgentState) => void;
	onTranscription?: (text: string) => void;
	onAudioChunk?: (base64Audio: string) => void;
	onError?: (error: string) => void;
	onProcessingTime?: (time: number | null) => void;
}

export class WebSocketServiceManager {
	private ws: WebSocket | null = null;
	private state: AgentState = "disconnected";
	private transcription: string = "";
	private error: string | null = null;
	private isConnected: boolean = false;
	private processingTime: number | null = null;
	private clientId: string;
	private callbacks: WebSocketServiceCallbacks;

	constructor(callbacks: WebSocketServiceCallbacks = {}) {
		this.clientId = `client_${Date.now()}_${Math.random()
			.toString(36)
			.substr(2, 9)}`;
		this.callbacks = callbacks;
	}

	connect(wsUrl?: string): void {
		if (this.ws?.readyState === WebSocket.OPEN) {
			return;
		}

		try {
			const url =
				wsUrl ||
				import.meta.env.VITE_WS_URL ||
				"ws://localhost:8000/ws";
			const ws = new WebSocket(url);

			ws.onopen = () => {
				console.log("WebSocket connected");
				this.isConnected = true;
				this.setState("connected");
				this.error = null;
				this.callbacks.onError?.(null as any);

				// Send initial connection message
				try {
					ws.send(
						JSON.stringify({
							type: "connect",
							client_id: this.clientId,
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
							this.setState(message.data as AgentState);
							// Store processing time if provided
							if (message.processing_time !== undefined) {
								this.processingTime = message.processing_time;
								this.callbacks.onProcessingTime?.(
									this.processingTime
								);
							}
							// Clear processing time when starting a new recording
							if (
								message.data === "listening" ||
								message.data === "processing"
							) {
								this.processingTime = null;
								this.callbacks.onProcessingTime?.(null);
							}
							break;
						case "transcription":
							console.log("📝 Transcription:", message.data);
							this.transcription = message.data;
							this.callbacks.onTranscription?.(message.data);
							break;
						case "audio_chunk":
							console.log(
								"🎵 Audio chunk received, length:",
								message.data?.length
							);
							this.callbacks.onAudioChunk?.(message.data);
							break;
						case "error":
							this.error = message.data;
							console.error("❌ WebSocket error:", message.data);
							this.callbacks.onError?.(message.data);
							break;
					}
				} catch (err) {
					console.error("Error parsing WebSocket message:", err);
				}
			};

			ws.onerror = (err) => {
				console.error("WebSocket error:", err);
				const errorMsg = "WebSocket connection error";
				this.error = errorMsg;
				this.setState("disconnected");
				this.isConnected = false;
				this.callbacks.onError?.(errorMsg);
			};

			ws.onclose = () => {
				console.log("WebSocket disconnected");
				this.setState("disconnected");
				this.isConnected = false;
			};

			this.ws = ws;
		} catch (err) {
			console.error("Failed to connect WebSocket:", err);
			const errorMsg = "Failed to connect to server";
			this.error = errorMsg;
			this.setState("disconnected");
			this.isConnected = false;
			this.callbacks.onError?.(errorMsg);
		}
	}

	disconnect(): void {
		if (this.ws) {
			this.ws.close();
			this.ws = null;
		}
		this.setState("disconnected");
		this.isConnected = false;
	}

	sendMessage(type: string, data: string): void {
		if (this.ws?.readyState === WebSocket.OPEN) {
			this.ws.send(
				JSON.stringify({
					type,
					data,
					client_id: this.clientId,
				})
			);
		} else {
			console.warn("WebSocket is not connected");
		}
	}

	private setState(newState: AgentState): void {
		this.state = newState;
		this.callbacks.onStateChange?.(newState);
	}

	getState(): AgentState {
		return this.state;
	}

	getTranscription(): string {
		return this.transcription;
	}

	getError(): string | null {
		return this.error;
	}

	getIsConnected(): boolean {
		return this.isConnected;
	}

	getProcessingTime(): number | null {
		return this.processingTime;
	}

	updateCallbacks(callbacks: Partial<WebSocketServiceCallbacks>): void {
		this.callbacks = { ...this.callbacks, ...callbacks };
	}

	cleanup(): void {
		this.disconnect();
		this.state = "disconnected";
		this.transcription = "";
		this.error = null;
		this.isConnected = false;
		this.processingTime = null;
	}
}
