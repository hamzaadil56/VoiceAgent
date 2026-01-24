import { useEffect, useRef, useState, useCallback } from "react";
import {
	WebSocketServiceManager,
	WebSocketServiceCallbacks,
} from "../services/WebSocketServiceManager";

export type AgentState =
	| "idle"
	| "listening"
	| "processing"
	| "speaking"
	| "connected"
	| "disconnected";

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

	const serviceRef = useRef<WebSocketServiceManager | null>(null);

	// Single useEffect for initialization
	useEffect(() => {
		const callbacks: WebSocketServiceCallbacks = {
			onStateChange: (newState) => {
				setState(newState);
				// Update isConnected based on state
				setIsConnected(newState !== "disconnected");
			},
			onTranscription: (text) => {
				setTranscription(text);
				onTranscription?.(text);
			},
			onAudioChunk: (base64Audio) => {
				onAudioChunk?.(base64Audio);
			},
			onError: (errorMsg) => {
				setError(errorMsg);
			},
			onProcessingTime: (time) => {
				setProcessingTime(time);
			},
		};

		serviceRef.current = new WebSocketServiceManager(callbacks);

		return () => {
			serviceRef.current?.cleanup();
			serviceRef.current = null;
		};
	}, []); // Empty deps - callbacks updated separately

	// Update callbacks when they change
	useEffect(() => {
		if (serviceRef.current) {
			serviceRef.current.updateCallbacks({
				onTranscription,
				onAudioChunk,
			});
		}
	}, [onAudioChunk, onTranscription]);

	const connect = useCallback(() => {
		serviceRef.current?.connect();
	}, []);

	const disconnect = useCallback(() => {
		serviceRef.current?.disconnect();
	}, []);

	const sendMessage = useCallback((type: string, data: string) => {
		serviceRef.current?.sendMessage(type, data);
	}, []);

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
