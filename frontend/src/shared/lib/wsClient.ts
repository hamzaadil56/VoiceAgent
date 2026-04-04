/** WebSocket client base for real-time communication */

type MessageHandler = (data: Record<string, unknown>) => void;
type StateChangeHandler = (state: WsState) => void;

export type WsState = "connecting" | "connected" | "disconnected" | "error";

export class WsClient {
	private ws: WebSocket | null = null;
	private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
	private handlers = new Map<string, MessageHandler[]>();
	private stateHandlers: StateChangeHandler[] = [];
	private _state: WsState = "disconnected";
	private reconnectAttempts = 0;
	private maxReconnectAttempts = 5;

	constructor(
		private url: string,
		private authToken?: string,
	) {}

	get state(): WsState {
		return this._state;
	}

	private setState(state: WsState) {
		this._state = state;
		this.stateHandlers.forEach((h) => h(state));
	}

	connect() {
		if (this.ws?.readyState === WebSocket.OPEN) return;

		this.setState("connecting");
		const wsBase = (
			import.meta.env.VITE_WS_URL ||
			import.meta.env.VITE_BACKEND_URL ||
			"http://localhost:8000"
		).replace(/^http/, "ws");

		this.ws = new WebSocket(`${wsBase}${this.url}`);

		this.ws.onopen = () => {
			this.reconnectAttempts = 0;
			if (this.authToken) {
				this.send({ type: "auth", token: this.authToken });
			}
			this.setState("connected");
		};

		this.ws.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data);
				const type = data.type as string;
				const handlers = this.handlers.get(type) || [];
				handlers.forEach((h) => h(data));

				// Also call wildcard handlers
				const wildcardHandlers = this.handlers.get("*") || [];
				wildcardHandlers.forEach((h) => h(data));
			} catch {
				// ignore parse errors
			}
		};

		this.ws.onclose = () => {
			this.setState("disconnected");
			this.tryReconnect();
		};

		this.ws.onerror = () => {
			this.setState("error");
		};
	}

	private tryReconnect() {
		if (this.reconnectAttempts >= this.maxReconnectAttempts) return;
		this.reconnectAttempts++;
		const delay = Math.min(1000 * 2 ** this.reconnectAttempts, 16000);
		this.reconnectTimer = setTimeout(() => this.connect(), delay);
	}

	send(data: Record<string, unknown>) {
		if (this.ws?.readyState === WebSocket.OPEN) {
			this.ws.send(JSON.stringify(data));
		}
	}

	sendBinary(data: ArrayBuffer | Blob) {
		if (this.ws?.readyState === WebSocket.OPEN) {
			this.ws.send(data);
		}
	}

	on(type: string, handler: MessageHandler) {
		const existing = this.handlers.get(type) || [];
		existing.push(handler);
		this.handlers.set(type, existing);
		return () => {
			const handlers = this.handlers.get(type) || [];
			this.handlers.set(
				type,
				handlers.filter((h) => h !== handler),
			);
		};
	}

	onStateChange(handler: StateChangeHandler) {
		this.stateHandlers.push(handler);
		return () => {
			this.stateHandlers = this.stateHandlers.filter((h) => h !== handler);
		};
	}

	disconnect() {
		if (this.reconnectTimer) {
			clearTimeout(this.reconnectTimer);
			this.reconnectTimer = null;
		}
		this.maxReconnectAttempts = 0; // prevent further reconnects
		if (this.ws) {
			this.ws.close();
			this.ws = null;
		}
		this.setState("disconnected");
	}
}
