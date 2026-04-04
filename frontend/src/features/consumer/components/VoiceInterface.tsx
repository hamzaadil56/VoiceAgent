import { useCallback, useEffect, useMemo } from "react";
import { useVoiceSession, type VoiceState } from "../hooks/useVoiceSession";
import { MessageBubble } from "./MessageBubble";

interface VoiceInterfaceProps {
	sessionId: string;
	sessionToken: string;
	onSwitchToChat?: () => void;
}

export function VoiceInterface({ sessionId, sessionToken, onSwitchToChat }: VoiceInterfaceProps) {
	const voice = useVoiceSession({ sessionId, sessionToken });

	useEffect(() => {
		voice.connect();
		return () => voice.disconnect();
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	const handleMicClick = useCallback(() => {
		if (!voice.initialAgentPlaybackDone) return;
		if (voice.state === "connected" || voice.state === "error") {
			void voice.startRecording();
		} else if (voice.state === "listening") {
			voice.stopRecording();
		} else if (voice.state === "disconnected") {
			voice.connect();
		}
	}, [voice]);

	const isCompleted = voice.state === "completed";

	const baseStateLabel: Record<VoiceState, string> = useMemo(
		() => ({
			disconnected: "Disconnected",
			connecting: "Connecting...",
			connected: "Listening will start automatically…",
			listening: "Listening…",
			processing: "Processing…",
			speaking: "Agent is speaking…",
			completed: "Form completed",
			error: "Tap mic to retry microphone",
		}),
		[],
	);

	const headline = useMemo(() => {
		if (voice.state === "connected" && !voice.initialAgentPlaybackDone) {
			return "Agent is getting ready…";
		}
		if (voice.state === "listening") {
			return voice.vadUserHasSpoken
				? "Listening… we'll stop when you pause"
				: "Listening… speak when ready";
		}
		return baseStateLabel[voice.state];
	}, [voice.state, voice.initialAgentPlaybackDone, voice.vadUserHasSpoken, baseStateLabel]);

	return (
		<div
			className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 overflow-hidden flex flex-col shadow-md"
			style={{ height: "75vh", maxHeight: "680px" }}
		>
			{/* Voice visualization area */}
			<div className="flex-1 flex flex-col items-center justify-center px-6 py-8 gap-6">
				{/* Sage waveform — visible while listening or speaking */}
				{(voice.state === "listening" || voice.state === "speaking") && (
					<div className="flex items-center gap-[3px] h-[36px]">
						{Array.from({ length: 12 }).map((_, i) => (
							<div
								key={i}
								className="w-[3px] rounded-sm bg-sage-500"
								style={{
									animation: `voice-wave 1s ease-in-out infinite`,
									animationDelay: `${i * 0.08}s`,
								}}
							/>
						))}
					</div>
				)}

				{/* Sage voice orb / mic button */}
				<button
					onClick={handleMicClick}
					disabled={
						voice.state === "processing" ||
						voice.state === "connecting" ||
						voice.state === "speaking" ||
						isCompleted ||
						!voice.initialAgentPlaybackDone
					}
					className="w-[72px] h-[72px] rounded-full border-none grid place-items-center cursor-pointer transition-all duration-150 text-white disabled:opacity-50 disabled:cursor-not-allowed"
					style={{
						background:
							voice.state === "speaking" ? "var(--clay-500)" : "var(--sage-500)",
						animation:
							(voice.state === "connected" || voice.state === "listening" || voice.state === "error") &&
							!isCompleted
								? "mic-pulse 2.2s ease infinite"
								: "none",
						boxShadow:
							voice.state === "speaking" ? "var(--shadow-clay)" : "var(--shadow-sage)",
					}}
					title={
						voice.state === "listening"
							? "Stop and send now"
							: voice.state === "error"
								? "Retry microphone"
								: "Start listening"
					}
				>
					{voice.state === "listening" ? (
						<svg className="w-7 h-7" fill="currentColor" viewBox="0 0 24 24">
							<rect x="6" y="6" width="12" height="12" rx="2" />
						</svg>
					) : voice.state === "speaking" ? (
						<svg width="28" height="28" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
							<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
							<path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" />
						</svg>
					) : (
						<svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z"
							/>
						</svg>
					)}
				</button>

				<p className="font-heading font-medium text-[18px] text-text-primary text-center max-w-md">
					{headline}
				</p>

				{voice.isHandsFree && voice.initialAgentPlaybackDone && !isCompleted && (
					<p className="text-[12px] text-text-secondary text-center max-w-sm">
						Hands-free: the mic turns on after the agent speaks. Pause ~1.5s to send your reply.
					</p>
				)}

				{voice.error && (
					<p className="text-[13px] mt-1 text-error">
						{voice.error}
					</p>
				)}

				{isCompleted && (
					<div className="inline-flex items-center gap-2 px-4 py-2 rounded-md font-medium text-[13px] bg-forest-100 text-forest-600">
						<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
							<path
								strokeLinecap="round"
								strokeLinejoin="round"
								d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
							/>
						</svg>
						Thank you for your responses!
					</div>
				)}
			</div>

			{/* Message history */}
			{voice.messages.length > 0 && (
				<div className="border-t border-stone-100 max-h-[30%] overflow-y-auto px-5 py-4 flex flex-col gap-2">
					{voice.messages.map((msg, i) => (
						<MessageBubble key={i} message={msg} />
					))}
				</div>
			)}

			{/* Controls */}
			<div className="border-t border-stone-100 p-4 flex justify-center gap-3">
				{onSwitchToChat && !isCompleted && (
					<button
						type="button"
						onClick={onSwitchToChat}
						className="px-4 py-[9px] rounded-md font-medium text-[13px] text-text-secondary bg-bg-base border-[0.5px] border-stone-200 hover:border-stone-300 hover:text-text-primary transition-all"
					>
						Switch to Chat
					</button>
				)}
			</div>
		</div>
	);
}
