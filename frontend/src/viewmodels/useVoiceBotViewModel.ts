import { useState, useEffect, useCallback, useRef } from "react";
import { AgentState } from "../hooks/useWebSocket";
import { VoiceBotViewModel, VoiceBotViewModelState } from "./VoiceBotViewModel";
import { AudioServiceManager } from "../services/AudioServiceManager";
import { WebSocketServiceManager } from "../services/WebSocketServiceManager";

export function useVoiceBotViewModel() {
	const [viewModelState, setViewModelState] =
		useState<VoiceBotViewModelState>({
			conversationHistory: [],
			effectiveState: "disconnected",
			isRecording: false,
			isPlaying: false,
			isInitialized: false,
			isConnected: false,
			error: null,
			processingTime: null,
			turnCount: 0,
		});

	const viewModelRef = useRef<VoiceBotViewModel | null>(null);
	const audioServiceRef = useRef<AudioServiceManager | null>(null);
	const wsServiceRef = useRef<WebSocketServiceManager | null>(null);
	const [isInitialized, setIsInitialized] = useState(false);
	const [isRecording, setIsRecording] = useState(false);
	const [backendState, setBackendState] =
		useState<AgentState>("disconnected");
	const [error, setError] = useState<string | null>(null);
	const [isConnected, setIsConnected] = useState(false);
	const [processingTime, setProcessingTime] = useState<number | null>(null);

	// Single useEffect for initialization
	useEffect(() => {
		// Create service managers
		audioServiceRef.current = new AudioServiceManager();
		wsServiceRef.current = new WebSocketServiceManager();

		// Initialize audio service
		const initAudio = async () => {
			try {
				await audioServiceRef.current!.initialize();
				setIsInitialized(true);
			} catch (error) {
				console.error("Failed to initialize audio service:", error);
			}
		};
		initAudio();

		// Create ViewModel with services
		viewModelRef.current = new VoiceBotViewModel(
			audioServiceRef.current,
			wsServiceRef.current,
			{
				onStateChange: (state) => {
					setViewModelState(state);
				},
			}
		);

		// Configure silence detection with default settings
		// Threshold: 0.01 (1% volume), Duration: 2000ms (2 seconds), Check: 100ms
		viewModelRef.current.configureSilenceDetection({
			threshold: 0.1,
			silenceDuration: 2000,
			checkInterval: 100,
		});

		// Set up WebSocket callbacks
		wsServiceRef.current.updateCallbacks({
			onAudioChunk: (base64Audio: string) => {
				if (viewModelRef.current) {
					viewModelRef.current.handleAudioChunk(base64Audio);
				}
			},
			onTranscription: (text: string) => {
				if (viewModelRef.current) {
					viewModelRef.current.handleTranscription(text);
				}
			},
			onStateChange: (state: AgentState) => {
				setBackendState(state);
				if (viewModelRef.current) {
					const shouldPlay =
						viewModelRef.current.handleBackendStateChange(state);
					if (shouldPlay) {
						// Trigger playback
						const playBufferedAudio = async () => {
							if (viewModelRef.current) {
								await viewModelRef.current.playBufferedAudio();
								viewModelRef.current.incrementTurnCount();
							}
						};
						playBufferedAudio();
					}
				}
			},
			onError: (errorMsg: string) => {
				setError(errorMsg);
			},
			onProcessingTime: (time: number | null) => {
				setProcessingTime(time);
			},
		});

		// Connect WebSocket
		wsServiceRef.current.connect();

		// Poll for state updates
		const interval = setInterval(() => {
			if (audioServiceRef.current) {
				setIsRecording(audioServiceRef.current.isRecording());
				// Note: isPlaying is managed by the service's play methods
				// We track it through the ViewModel state instead
			}
			if (wsServiceRef.current) {
				setIsConnected(wsServiceRef.current.getIsConnected());
			}
		}, 100);

		return () => {
			clearInterval(interval);
			viewModelRef.current = null;
			audioServiceRef.current?.cleanup();
			wsServiceRef.current?.cleanup();
			audioServiceRef.current = null;
			wsServiceRef.current = null;
		};
	}, []);

	// Update ViewModel with state changes
	useEffect(() => {
		if (viewModelRef.current) {
			viewModelRef.current.updateExternalState({
				isRecording,
				isPlaying: viewModelState.isPlaying, // Get from ViewModel state
				isInitialized,
				isConnected,
				error,
				processingTime,
				backendState,
			});
		}
	}, [
		isRecording,
		viewModelState.isPlaying,
		isInitialized,
		isConnected,
		error,
		processingTime,
		backendState,
	]);

	// Expose ViewModel methods
	const startRecordingHandler = useCallback(async () => {
		if (viewModelRef.current) {
			await viewModelRef.current.startRecording();
		}
	}, []);

	const stopRecordingHandler = useCallback(async () => {
		if (viewModelRef.current) {
			await viewModelRef.current.stopRecording();
		}
	}, []);

	const handleTextSubmit = useCallback((text: string) => {
		if (viewModelRef.current) {
			viewModelRef.current.handleTextSubmit(text);
		}
	}, []);

	const getStateLabel = useCallback(() => {
		if (viewModelRef.current) {
			return viewModelRef.current.getStateLabel();
		}
		return "Unknown";
	}, []);

	const canStartRecording = useCallback(() => {
		if (viewModelRef.current) {
			return viewModelRef.current.canStartRecording();
		}
		return false;
	}, []);

	return {
		// State
		...viewModelState,
		// Methods
		startRecording: startRecordingHandler,
		stopRecording: stopRecordingHandler,
		handleTextSubmit,
		getStateLabel,
		canStartRecording,
		// Direct access to some values for convenience
		isRecording,
		isPlaying: viewModelState.isPlaying,
	};
}
