import { AgentState } from "../hooks/useWebSocket";
import { AudioServiceManager } from "../services/AudioServiceManager";
import { WebSocketServiceManager } from "../services/WebSocketServiceManager";

export interface ConversationMessage {
	role: "user" | "agent";
	text: string;
}

export interface VoiceBotViewModelState {
	conversationHistory: ConversationMessage[];
	effectiveState: AgentState;
	isRecording: boolean;
	isPlaying: boolean;
	isInitialized: boolean;
	isConnected: boolean;
	error: string | null;
	processingTime: number | null;
	turnCount: number;
}

export interface VoiceBotViewModelCallbacks {
	onStateChange?: (state: VoiceBotViewModelState) => void;
}

export class VoiceBotViewModel {
	private conversationHistory: ConversationMessage[] = [];
	private effectiveState: AgentState = "disconnected";
	private audioChunksBuffer: string[] = [];
	private pcmChunksBuffer: string[] = [];
	private isCollecting = false;
	private isPlayingRef = false;
	private turnCount = 0;
	private maxTurns = 5; // Default, will be updated from settings
	private callbacks: VoiceBotViewModelCallbacks;

	// Services
	private audioService: AudioServiceManager;
	private wsService: WebSocketServiceManager;

	// External state (managed by hooks)
	private isRecording = false;
	private isPlaying = false;
	private isInitialized = false;
	private isConnected = false;
	private error: string | null = null;
	private processingTime: number | null = null;
	private backendState: AgentState = "disconnected";

	constructor(
		audioService: AudioServiceManager,
		wsService: WebSocketServiceManager,
		callbacks: VoiceBotViewModelCallbacks = {}
	) {
		this.audioService = audioService;
		this.wsService = wsService;
		this.callbacks = callbacks;
	}

	// Update external state from hooks
	updateExternalState(
		updates: Partial<{
			isRecording: boolean;
			isPlaying: boolean;
			isInitialized: boolean;
			isConnected: boolean;
			error: string | null;
			processingTime: number | null;
			backendState: AgentState;
		}>
	) {
		if (updates.isRecording !== undefined)
			this.isRecording = updates.isRecording;
		if (updates.isPlaying !== undefined) this.isPlaying = updates.isPlaying;
		if (updates.isInitialized !== undefined)
			this.isInitialized = updates.isInitialized;
		if (updates.isConnected !== undefined)
			this.isConnected = updates.isConnected;
		if (updates.error !== undefined) this.error = updates.error;
		if (updates.processingTime !== undefined)
			this.processingTime = updates.processingTime;
		if (updates.backendState !== undefined)
			this.backendState = updates.backendState;
		this.notifyStateChange();
	}

	// Handle transcription from backend
	handleTranscription(text: string) {
		if (text) {
			this.conversationHistory = [
				...this.conversationHistory,
				{ role: "agent", text },
			];
			this.notifyStateChange();
		}
	}

	// Handle audio chunk from backend
	handleAudioChunk(base64Audio: string) {
		console.log("📥 PCM Audio chunk received:", {
			chunkSize: base64Audio.length,
			totalChunks: this.pcmChunksBuffer.length + 1,
			preview: base64Audio.substring(0, 50),
		});

		// Start collecting chunks
		if (!this.isCollecting) {
			console.log("🗣️ Starting audio collection");
			this.isCollecting = true;
			this.pcmChunksBuffer = [];

			if (this.isRecording) {
				console.log("⏹️ Stopping recording before playback...");
				this.audioService.stopRecording().catch((err) => {
					console.error("Error stopping recording:", err);
				});
			}
			this.effectiveState = "speaking";
			this.notifyStateChange();
		}

		// Add chunk to buffer
		this.pcmChunksBuffer.push(base64Audio);
		console.log(`📦 Buffered chunk ${this.pcmChunksBuffer.length}`);
	}

	// Play buffered audio when backend signals completion
	async playBufferedAudio() {
		if (this.pcmChunksBuffer.length === 0) {
			console.log("⚠️ No audio chunks to play");
			return;
		}

		console.log(
			`🎵 Playing ${this.pcmChunksBuffer.length} buffered chunks as complete audio`
		);
		this.isPlayingRef = true;

		try {
			// Play all chunks as one complete audio
			await this.audioService.playPCMChunks(this.pcmChunksBuffer);
			console.log("✅ Complete audio played successfully");
		} catch (err) {
			console.error("❌ Audio playback error:", err);
		} finally {
			// Reset state
			this.isPlayingRef = false;
			this.isCollecting = false;
			this.pcmChunksBuffer = [];
			this.effectiveState = "idle";
			console.log("🔄 Returned to IDLE state");
			this.notifyStateChange();

			// Automatically restart listening if max turns not reached
			// Note: turnCount was already incremented before this method was called
			if (this.turnCount < this.maxTurns) {
				console.log(
					"🔄 Auto-restarting listening after agent finished speaking"
				);
				// Small delay to ensure state is properly reset
				setTimeout(() => {
					// Double-check before starting (in case turnCount changed)
					if (this.turnCount < this.maxTurns) {
						this.startRecording().catch((err) => {
							console.error(
								"Error auto-restarting recording:",
								err
							);
						});
					} else {
						console.log(
							`⚠️ Max turns (${this.maxTurns}) reached. Session stopped.`
						);
					}
				}, 500);
			} else {
				console.log(
					`⚠️ Max turns (${this.maxTurns}) reached. Session stopped.`
				);
			}
		}
	}

	// Handle backend state changes
	handleBackendStateChange(newState: AgentState) {
		if (newState === "idle" && this.isCollecting) {
			console.log(
				"🏁 Backend sent 'idle' - all chunks received, playing audio..."
			);
			// The actual playback will be triggered by the hook
			return true; // Signal that playback should be triggered
		} else if (
			!this.isPlayingRef &&
			!this.isPlaying &&
			!this.isCollecting
		) {
			this.effectiveState = newState;
			this.notifyStateChange();
		}
		return false;
	}

	// Handle silence detected - auto-stop recording
	private async handleSilenceDetected() {
		if (!this.isRecording) {
			return;
		}

		console.log("🔇 Silence detected, auto-stopping recording...");
		await this.stopRecording();
	}

	// Start recording
	async startRecording() {
		if (!this.isInitialized || !this.isConnected) {
			alert("Audio not initialized or not connected to server");
			return;
		}

		// Check if max turns reached
		if (this.turnCount >= this.maxTurns) {
			console.log(
				`Cannot start recording - max turns (${this.maxTurns}) reached`
			);
			return;
		}

		// Only allow starting when idle or connected, not during processing/speaking
		if (
			this.effectiveState !== "idle" &&
			this.effectiveState !== "connected"
		) {
			console.log("Cannot start recording - agent is busy");
			return;
		}

		if (this.isPlaying || this.isPlayingRef) {
			console.log("Cannot start recording while audio is playing");
			return;
		}

		if (this.isRecording) {
			console.log("Already recording");
			return;
		}

		try {
			// Clear buffer for new recording
			this.audioChunksBuffer = [];
			console.log("🎤 Starting recording - buffering chunks locally");

			// Set up silence detection callback
			this.audioService.setCallbacks({
				onSilenceDetected: () => {
					this.handleSilenceDetected();
				},
			});

			// Start recording with chunk callback
			await this.audioService.startRecording(async (base64Chunk) => {
				// Buffer chunks locally instead of streaming
				this.audioChunksBuffer.push(base64Chunk);
				console.log(
					`📦 Buffered audio chunk ${this.audioChunksBuffer.length}`
				);
			});

			// Notify backend that recording started
			this.wsService.sendMessage("start_recording", "");
			console.log("✅ Recording started with silence detection");
		} catch (error) {
			console.error("Error starting recording:", error);
			alert(
				"Failed to start recording. Please check microphone permissions."
			);
		}
	}

	// Stop recording
	async stopRecording() {
		if (!this.isRecording) return;

		console.log("⏹️ Stopping recording...");
		try {
			// Stop recording (this returns the complete blob)
			// This will also stop silence detection monitoring
			const finalAudio = await this.audioService.stopRecording();

			console.log(
				`📤 Sending ${this.audioChunksBuffer.length} buffered chunks to backend`
			);

			// Send all buffered chunks to backend
			for (let i = 0; i < this.audioChunksBuffer.length; i++) {
				this.wsService.sendMessage(
					"audio_chunk",
					this.audioChunksBuffer[i]
				);
			}

			// Send final audio blob and stop signal
			this.wsService.sendMessage("stop_recording", finalAudio);

			// Clear buffer
			this.audioChunksBuffer = [];
			console.log("✅ Recording stopped and sent to backend");
		} catch (error) {
			console.error("Error stopping recording:", error);
		}
	}

	// Configure silence detection
	configureSilenceDetection(config: {
		threshold?: number;
		silenceDuration?: number;
		checkInterval?: number;
	}) {
		this.audioService.setSilenceConfig(config);
	}

	// Handle text message submission
	handleTextSubmit(text: string) {
		if (!text || !this.isConnected) return;

		this.conversationHistory = [
			...this.conversationHistory,
			{ role: "user", text },
		];
		this.wsService.sendMessage("text_message", text);
		this.notifyStateChange();
	}

	// Increment turn count after playback
	incrementTurnCount() {
		this.turnCount += 1;
		if (this.turnCount >= this.maxTurns) {
			console.log(
				`⚠️ Turn limit reached (${this.maxTurns} turns). Session stopped.`
			);
		}
		this.notifyStateChange();
	}

	// Set max turns from settings
	setMaxTurns(maxTurns: number) {
		this.maxTurns = Math.min(Math.max(1, maxTurns), 5); // Clamp between 1 and 5
		console.log(`📊 Max turns set to: ${this.maxTurns}`);
	}

	// Get current state
	getState(): VoiceBotViewModelState {
		return {
			conversationHistory: this.conversationHistory,
			effectiveState: this.effectiveState,
			isRecording: this.isRecording,
			isPlaying: this.isPlaying,
			isInitialized: this.isInitialized,
			isConnected: this.isConnected,
			error: this.error,
			processingTime: this.processingTime,
			turnCount: this.turnCount,
		};
	}

	// Get state label for UI
	getStateLabel(): string {
		if (!this.isConnected) return "Disconnected";
		if (!this.isInitialized) return "Initializing audio...";

		if (this.isPlaying || this.isPlayingRef) return "🔊 Speaking...";

		switch (this.effectiveState) {
			case "idle":
				return this.isRecording
					? "🎤 Listening... (Tap circle to stop)"
					: "Click circle to start";
			case "listening":
				return "🎤 Listening...";
			case "processing":
				return "Processing...";
			case "speaking":
				return "🔊 Speaking...";
			case "connected":
				return this.isRecording
					? "🎤 Listening... (Tap circle to stop)"
					: "Click circle to start";
			case "disconnected":
				return "Disconnected";
			default:
				return "Unknown";
		}
	}

	// Check if can start recording
	canStartRecording(): boolean {
		return (
			this.isInitialized &&
			this.isConnected &&
			!this.isPlaying &&
			!this.isPlayingRef &&
			!this.isRecording &&
			(this.effectiveState === "idle" ||
				this.effectiveState === "connected")
		);
	}

	// Check if should trigger playback
	shouldTriggerPlayback(): boolean {
		return this.backendState === "idle" && this.isCollecting;
	}

	// Get PCM chunks for playback
	getPCMChunks(): string[] {
		return [...this.pcmChunksBuffer];
	}

	// Get max turns
	getMaxTurns(): number {
		return this.maxTurns;
	}

	// Notify state change
	private notifyStateChange() {
		if (this.callbacks.onStateChange) {
			this.callbacks.onStateChange(this.getState());
		}
	}
}
