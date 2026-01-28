import { useEffect, useRef } from "react";
import { AudioServiceManager } from "../services/AudioServiceManager";
import { WebSocketServiceManager } from "../services/WebSocketServiceManager";

export function useServices() {
	const audioServiceRef = useRef<AudioServiceManager | null>(null);
	const wsServiceRef = useRef<WebSocketServiceManager | null>(null);

	// Single useEffect for all service initialization
	useEffect(() => {
		// Create service managers
		audioServiceRef.current = new AudioServiceManager();
		wsServiceRef.current = new WebSocketServiceManager();

		// Initialize audio service
		const initAudio = async () => {
			try {
				await audioServiceRef.current!.initialize();
			} catch (error) {
				console.error("Failed to initialize audio service:", error);
			}
		};
		initAudio();

		// Connect WebSocket
		wsServiceRef.current.connect();

		return () => {
			audioServiceRef.current?.cleanup();
			wsServiceRef.current?.cleanup();
			audioServiceRef.current = null;
			wsServiceRef.current = null;
		};
	}, []);

	return {
		audioService: audioServiceRef.current,
		wsService: wsServiceRef.current,
	};
}
