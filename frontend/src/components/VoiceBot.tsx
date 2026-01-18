import { useState, useEffect, useCallback, useRef } from "react";
import { useWebSocket, AgentState } from "../hooks/useWebSocket";
import { useAudio } from "../hooks/useAudio";
import AnimatedCircle from "./AnimatedCircle";

export default function VoiceBot() {
	const [audioChunks, setAudioChunks] = useState<string[]>([]);
	const [conversationHistory, setConversationHistory] = useState<
		Array<{ role: "user" | "agent"; text: string }>
	>([]);
	const [effectiveState, setEffectiveState] =
		useState<AgentState>("disconnected");
	const audioQueueRef = useRef<string[]>([]);
	const isPlayingRef = useRef(false);
	const turnCountRef = useRef(0); // Track number of turns for MacBook performance

	const {
		isInitialized,
		isRecording,
		startRecording,
		stopRecording,
		playPCMChunks,
		isPlaying,
	} = useAudio();

	const handleTranscription = useCallback((text: string) => {
		if (text) {
			setConversationHistory((prev) => [
				...prev,
				{ role: "agent", text },
			]);
		}
	}, []);

	// Buffer PCM chunks and play complete audio once
	const pcmChunksRef = useRef<string[]>([]);
	const isCollectingRef = useRef(false);

	const handleAudioChunk = useCallback(
		async (base64Audio: string) => {
			console.log("📥 PCM Audio chunk received:", {
				chunkSize: base64Audio.length,
				totalChunks: pcmChunksRef.current.length + 1,
				preview: base64Audio.substring(0, 50),
			});

			// Start collecting chunks
			if (!isCollectingRef.current) {
				console.log("🗣️ Starting audio collection");
				isCollectingRef.current = true;
				pcmChunksRef.current = [];

				if (isRecording) {
					console.log("⏹️ Stopping recording before playback...");
					try {
						await stopRecording();
					} catch (err) {
						console.error("Error stopping recording:", err);
					}
				}
				setEffectiveState("speaking");
			}

			// Add chunk to buffer
			pcmChunksRef.current.push(base64Audio);
			console.log(`📦 Buffered chunk ${pcmChunksRef.current.length}`);
		},
		[isRecording, stopRecording]
	);

	// Play buffered audio when backend signals completion
	const playBufferedAudio = useCallback(async () => {
		if (pcmChunksRef.current.length === 0) {
			console.log("⚠️ No audio chunks to play");
			return;
		}

		console.log(
			`🎵 Playing ${pcmChunksRef.current.length} buffered chunks as complete audio`
		);
		isPlayingRef.current = true;

		try {
			// Play all chunks as one complete audio
			await playPCMChunks(pcmChunksRef.current);
			console.log("✅ Complete audio played successfully");
		} catch (err) {
			console.error("❌ Audio playback error:", err);
		} finally {
			// Reset state
			isPlayingRef.current = false;
			isCollectingRef.current = false;
			pcmChunksRef.current = [];
			setEffectiveState("idle");
			console.log("🔄 Returned to IDLE state");
		}
	}, [playPCMChunks]);

	const { connect, disconnect, sendMessage, state, error, isConnected } =
		useWebSocket(handleAudioChunk, handleTranscription);

	useEffect(() => {
		connect();
		return () => {
			disconnect();
		};
	}, []);

	// Sync backend state with frontend
	// When backend sends "idle" after speaking, play buffered audio
	useEffect(() => {
		if (state === "idle" && isCollectingRef.current) {
			console.log(
				"🏁 Backend sent 'idle' - all chunks received, playing audio..."
			);
			playBufferedAudio();

			// Increment turn count after playback
			turnCountRef.current += 1;
			if (turnCountRef.current >= 3) {
				console.log(
					"⚠️ Turn limit reached (3 turns). Please refresh to continue."
				);
			}
		} else if (
			!isPlayingRef.current &&
			!isPlaying &&
			!isCollectingRef.current
		) {
			setEffectiveState(state);
		}
	}, [state, isPlaying, playBufferedAudio]);

	// Clear audio chunks when playback completes
	useEffect(() => {
		if (effectiveState !== "speaking" && audioChunks.length > 0) {
			setAudioChunks([]);
			audioQueueRef.current = [];
		}
	}, [effectiveState, audioChunks.length]);

	// Auto-start recording DISABLED - user must click circle to start

	// Reset auto-start flag when state becomes idle and audio stops
	// DISABLED: Single turn only - no auto-restart
	// useEffect(() => {
	// 	if (
	// 		effectiveState === "idle" &&
	// 		!isRecording &&
	// 		!isPlaying &&
	// 		!isPlayingRef.current &&
	// 		isConnected &&
	// 		isInitialized
	// 	) {
	// 		const timer = setTimeout(() => {
	// 			hasAutoStartedRef.current = false;
	// 		}, 300);
	// 		return () => clearTimeout(timer);
	// 	}
	// }, [effectiveState, isRecording, isPlaying, isConnected, isInitialized]);

	// Buffer audio chunks locally (same as PCM playback strategy)
	const audioChunksBufferRef = useRef<string[]>([]);

	const handleStartRecording = async () => {
		if (!isInitialized || !isConnected) {
			alert("Audio not initialized or not connected to server");
			return;
		}

		// Only allow starting when idle or connected, not during processing/speaking
		if (effectiveState !== "idle" && effectiveState !== "connected") {
			console.log("Cannot start recording - agent is busy");
			return;
		}

		if (isPlaying || isPlayingRef.current) {
			console.log("Cannot start recording while audio is playing");
			return;
		}

		if (isRecording) {
			console.log("Already recording");
			return;
		}

		try {
			// Clear buffer for new recording
			audioChunksBufferRef.current = [];
			console.log("🎤 Starting recording - buffering chunks locally");

			// Start recording with chunk callback
			await startRecording(async (base64Chunk) => {
				// Buffer chunks locally instead of streaming
				audioChunksBufferRef.current.push(base64Chunk);
				console.log(
					`📦 Buffered audio chunk ${audioChunksBufferRef.current.length}`
				);
			});

			// Notify backend that recording started
			sendMessage("start_recording", "");
			console.log("✅ Recording started");
		} catch (error) {
			console.error("Error starting recording:", error);
			alert(
				"Failed to start recording. Please check microphone permissions."
			);
		}
	};

	const handleStopRecording = async () => {
		if (!isRecording) return;

		console.log("⏹️ Stopping recording...");
		try {
			// Stop recording (this returns the complete blob)
			const finalAudio = await stopRecording();

			console.log(
				`📤 Sending ${audioChunksBufferRef.current.length} buffered chunks to backend`
			);

			// Send all buffered chunks to backend
			for (let i = 0; i < audioChunksBufferRef.current.length; i++) {
				sendMessage("audio_chunk", audioChunksBufferRef.current[i]);
			}

			// Send final audio blob and stop signal
			sendMessage("stop_recording", finalAudio);

			// Clear buffer
			audioChunksBufferRef.current = [];
			console.log("✅ Recording stopped and sent to backend");
		} catch (error) {
			console.error("Error stopping recording:", error);
		}
	};

	const handleTextSubmit = (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		const form = e.currentTarget;
		const input = form.querySelector("input") as HTMLInputElement;
		const text = input.value.trim();

		if (!text || !isConnected) return;

		setConversationHistory((prev) => [...prev, { role: "user", text }]);
		sendMessage("text_message", text);
		input.value = "";
	};

	const getStateLabel = (): string => {
		if (!isConnected) return "Disconnected";
		if (!isInitialized) return "Initializing audio...";

		if (isPlaying || isPlayingRef.current) return "🔊 Speaking...";

		switch (effectiveState) {
			case "idle":
				return isRecording
					? "🎤 Listening... (Tap circle to stop)"
					: "Click circle to start";
			case "listening":
				return "🎤 Listening...";
			case "processing":
				return "Processing...";
			case "speaking":
				return "🔊 Speaking...";
			case "connected":
				return isRecording
					? "🎤 Listening... (Tap circle to stop)"
					: "Click circle to start";
			case "disconnected":
				return "Disconnected";
			default:
				return "Unknown";
		}
	};

	return (
		<div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8">
			{/* Status and Circle */}
			<div className="flex flex-col items-center mb-8">
				<AnimatedCircle
					state={effectiveState}
					size={200}
					onClick={
						isRecording
							? handleStopRecording
							: effectiveState === "idle" ||
							  effectiveState === "connected"
							? handleStartRecording
							: undefined // Disable click during processing/speaking
					}
				/>
				<p className="mt-4 text-white text-lg font-semibold">
					{getStateLabel()}
				</p>
				{!isRecording &&
					!isPlaying &&
					!isPlayingRef.current &&
					(effectiveState === "idle" ||
						effectiveState === "connected") && (
						<p className="mt-2 text-blue-300 text-sm">
							👆 Tap the circle above to start talking
						</p>
					)}
				{isRecording && !isPlaying && !isPlayingRef.current && (
					<p className="mt-2 text-green-300 text-sm animate-pulse">
						✓ Listening - Tap circle or "Stop" when you finish
						speaking
					</p>
				)}
				{turnCountRef.current >= 3 && (
					<p className="mt-2 text-yellow-300 text-sm font-semibold">
						⚠️ Turn limit reached. Please refresh to continue.
					</p>
				)}
				{error && <p className="mt-2 text-red-300 text-sm">{error}</p>}
			</div>

			{/* Controls */}
			<div className="flex justify-center gap-4 mb-8">
				{isRecording ? (
					<button
						onClick={handleStopRecording}
						disabled={isPlaying || isPlayingRef.current}
						className="px-8 py-3 bg-red-500 hover:bg-red-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-all shadow-lg hover:shadow-xl"
					>
						⏹️ Stop & Send
					</button>
				) : (
					<button
						onClick={handleStartRecording}
						disabled={
							!isInitialized ||
							!isConnected ||
							isPlaying ||
							isPlayingRef.current ||
							(effectiveState !== "idle" &&
								effectiveState !== "connected")
						}
						className="px-8 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-all shadow-lg hover:shadow-xl"
					>
						🎤 Start Listening
					</button>
				)}
			</div>

			{/* Text Input Alternative */}
			<form onSubmit={handleTextSubmit} className="mb-6">
				<div className="flex gap-2">
					<input
						type="text"
						placeholder="Or type your message here..."
						disabled={!isConnected}
						className="flex-1 px-4 py-3 bg-white/20 text-white placeholder-white/60 rounded-lg border border-white/30 focus:outline-none focus:ring-2 focus:ring-white/50 disabled:opacity-50"
					/>
					<button
						type="submit"
						disabled={!isConnected}
						className="px-6 py-3 bg-purple-500 hover:bg-purple-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-all"
					>
						Send
					</button>
				</div>
			</form>

			{/* Conversation History */}
			{conversationHistory.length > 0 && (
				<div className="bg-white/5 rounded-lg p-4 max-h-64 overflow-y-auto">
					<h3 className="text-white font-semibold mb-3">
						Conversation
					</h3>
					<div className="space-y-2">
						{conversationHistory.map((msg, idx) => (
							<div
								key={idx}
								className={`p-2 rounded ${
									msg.role === "user"
										? "bg-blue-500/20 text-blue-100"
										: "bg-green-500/20 text-green-100"
								}`}
							>
								<span className="font-semibold">
									{msg.role === "user" ? "You: " : "Agent: "}
								</span>
								{msg.text}
							</div>
						))}
					</div>
				</div>
			)}

			{/* Connection Status */}
			<div className="mt-4 text-center">
				<span
					className={`inline-block w-3 h-3 rounded-full mr-2 ${
						isConnected ? "bg-green-400" : "bg-red-400"
					}`}
				/>
				<span className="text-white/80 text-sm">
					{isConnected ? "Connected" : "Disconnected"}
				</span>
			</div>
		</div>
	);
}
