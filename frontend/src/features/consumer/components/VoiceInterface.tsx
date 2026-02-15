/** Voice interface for consumer form sessions */
import { useCallback, useEffect } from "react";
import AnimatedCircle from "../../../components/AnimatedCircle";
import type { AgentState } from "../../../hooks/useWebSocket";
import { useVoiceSession, type VoiceState } from "../hooks/useVoiceSession";
import { MessageBubble } from "./MessageBubble";

interface VoiceInterfaceProps {
	sessionId: string;
	sessionToken: string;
	onSwitchToChat?: () => void;
}

/** Map VoiceState to AnimatedCircle's AgentState */
function mapToAgentState(state: VoiceState): AgentState {
	switch (state) {
		case "listening":
			return "listening";
		case "processing":
			return "processing";
		case "speaking":
			return "speaking";
		case "connected":
			return "connected";
		case "connecting":
			return "idle";
		case "completed":
			return "idle";
		case "error":
			return "disconnected";
		case "disconnected":
		default:
			return "disconnected";
	}
}

export function VoiceInterface({
	sessionId,
	sessionToken,
	onSwitchToChat,
}: VoiceInterfaceProps) {
	const voice = useVoiceSession({
		sessionId,
		sessionToken,
	});

	// Auto-connect on mount
	useEffect(() => {
		voice.connect();
		return () => voice.disconnect();
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	const handleCircleClick = useCallback(() => {
		if (voice.state === "connected" || voice.state === "speaking") {
			voice.startRecording();
		} else if (voice.state === "listening") {
			voice.stopRecording();
		} else if (voice.state === "disconnected" || voice.state === "error") {
			voice.connect();
		}
	}, [voice]);

	const agentState = mapToAgentState(voice.state);
	const isCompleted = voice.state === "completed";

	const stateLabel = {
		disconnected: "Disconnected",
		connecting: "Connecting...",
		connected: "Tap to speak",
		listening: "Listening... tap to stop",
		processing: "Processing...",
		speaking: "Speaking...",
		completed: "Form completed",
		error: "Error",
	}[voice.state];

	return (
		<div className="glass-elevated rounded-2xl border border-border/40 overflow-hidden flex flex-col" style={{ height: "70vh", maxHeight: "600px" }}>
			{/* Voice visualization area */}
			<div className="flex-1 flex flex-col items-center justify-center px-6 py-4">
				{/* Circle */}
				<div className="mb-6">
					<AnimatedCircle
						state={agentState}
						audioLevel={voice.audioLevel}
						size={160}
						onClick={handleCircleClick}
						isSpinning={voice.state === "connecting"}
					/>
				</div>

				{/* State label */}
				<p className="text-text-secondary text-sm mb-1">{stateLabel}</p>

				{voice.error && (
					<p className="text-error text-sm mt-1">{voice.error}</p>
				)}

				{isCompleted && (
					<div className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-success/10 text-success">
						<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
							<path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
						</svg>
						<span className="font-medium">Thank you for your responses!</span>
					</div>
				)}
			</div>

			{/* Message history (scrollable, compact) */}
			{voice.messages.length > 0 && (
				<div className="border-t border-border/40 max-h-[30%] overflow-y-auto p-4 space-y-2">
					{voice.messages.map((msg, i) => (
						<MessageBubble key={i} message={msg} />
					))}
				</div>
			)}

			{/* Controls */}
			<div className="border-t border-border/40 p-4 flex justify-center gap-3">
				{voice.state === "connected" && (
					<button
						onClick={voice.startRecording}
						className="px-5 py-3 rounded-xl bg-accent-primary text-bg-primary font-semibold hover:opacity-90"
					>
						<span className="flex items-center gap-2">
							<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
								<path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z" />
							</svg>
							Start Speaking
						</span>
					</button>
				)}
				{voice.state === "listening" && (
					<button
						onClick={voice.stopRecording}
						className="px-5 py-3 rounded-xl bg-error text-white font-semibold hover:opacity-90"
					>
						<span className="flex items-center gap-2">
							<svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
								<rect x="6" y="6" width="12" height="12" rx="2" />
							</svg>
							Stop Recording
						</span>
					</button>
				)}
				{onSwitchToChat && !isCompleted && (
					<button
						onClick={onSwitchToChat}
						className="px-4 py-3 rounded-xl glass border border-border text-text-secondary hover:text-text-primary"
					>
						Switch to Chat
					</button>
				)}
			</div>
		</div>
	);
}
