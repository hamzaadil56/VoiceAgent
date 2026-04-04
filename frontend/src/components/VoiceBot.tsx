import AnimatedCircle from "./AnimatedCircle";
import { useVoiceBotViewModel } from "../viewmodels/useVoiceBotViewModel";

export default function VoiceBot() {
	const {
		conversationHistory,
		effectiveState,
		isRecording,
		isPlaying,
		audioLevel,
		isConnected,
		isSpinning,
		error,
		processingTime,
		turnCount,
		startRecording,
		stopRecording,
		getStateLabel,
		getMaxTurns,
	} = useVoiceBotViewModel();

	const handleStartRecording = async () => {
		await startRecording();
	};

	const handleStopRecording = async () => {
		await stopRecording();
	};

	return (
		<div className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 shadow-md p-10">
			{/* Status and Circle */}
			<div className="flex flex-col items-center mb-10">
				<AnimatedCircle
					state={effectiveState}
					audioLevel={audioLevel ?? 0}
					size={220}
					isSpinning={isSpinning}
					onClick={
						isSpinning
							? undefined
							: turnCount >= getMaxTurns()
							? undefined
							: isRecording
							? handleStopRecording
							: effectiveState === "idle" ||
							  effectiveState === "connected"
							? handleStartRecording
							: undefined
					}
				/>
				<p className="mt-6 text-text-primary text-xl font-heading font-semibold">
					{getStateLabel()}
				</p>
				{processingTime !== null && (
					<div className="mt-3 flex items-center gap-2 px-4 py-2 bg-stone-50 rounded-full">
						<div className="w-1.5 h-1.5 rounded-full bg-forest-500 animate-pulse"></div>
						<p className="text-forest-600 text-sm font-medium">
							Processing: {processingTime}s
						</p>
					</div>
				)}
				{!isRecording &&
					!isPlaying &&
					(effectiveState === "idle" ||
						effectiveState === "connected") &&
					turnCount < getMaxTurns() && (
						<p className="mt-4 text-text-secondary text-sm animate-fade-in">
							Tap the circle above to start talking
						</p>
					)}
				{isRecording && !isPlaying && (
					<div className="mt-4 flex items-center gap-2 px-4 py-2 bg-forest-50 rounded-full border border-forest-200">
						<div className="w-2 h-2 rounded-full bg-forest-500 animate-pulse"></div>
						<p className="text-forest-600 text-sm font-medium animate-pulse">
							Listening — Tap circle when finished
						</p>
					</div>
				)}
				{turnCount >= getMaxTurns() && (
					<div className="mt-4 px-5 py-3 bg-stone-50 rounded-md border border-stone-200">
						<p className="text-warning text-sm font-medium text-center">
							Turn limit reached ({getMaxTurns()} turns). Refresh
							to continue.
						</p>
					</div>
				)}
				{turnCount > 0 && turnCount < getMaxTurns() && (
					<div className="mt-4 px-4 py-2 bg-stone-50 rounded-full">
						<p className="text-text-tertiary text-xs font-medium tracking-wide uppercase">
							Turn {turnCount} of {getMaxTurns()}
						</p>
					</div>
				)}
				{error && (
					<div className="mt-4 px-5 py-3 rounded-md" style={{ background: "var(--error-bg)", border: "1px solid var(--error-border)" }}>
						<p className="text-error text-sm">{error}</p>
					</div>
				)}
			</div>

			{/* Conversation History */}
			{conversationHistory.length > 0 && (
				<div className="bg-stone-50 rounded-lg p-6 max-h-80 overflow-y-auto border-[0.5px] border-stone-100">
					<h3 className="text-text-primary font-heading font-medium mb-4 text-lg">
						Conversation
					</h3>
					<div className="space-y-3">
						{conversationHistory.map((msg, idx) => (
							<div
								key={idx}
								className={`p-4 rounded-md border transition-all duration-300 ${
									msg.role === "user"
										? "bg-forest-50 border-forest-200 text-text-primary"
										: "bg-clay-50 border-clay-200 text-text-primary"
								}`}
							>
								<span className="font-medium text-xs uppercase tracking-wider mb-1 block opacity-70">
									{msg.role === "user" ? "You" : "Agent"}
								</span>
								<p className="text-sm leading-relaxed">
									{msg.text}
								</p>
							</div>
						))}
					</div>
				</div>
			)}

			{/* Connection Status */}
			<div className="mt-6 text-center">
				<div className="inline-flex items-center gap-2 px-4 py-2 bg-stone-50 rounded-full">
					<span
						className={`inline-block w-2.5 h-2.5 rounded-full ${
							isConnected
								? "bg-forest-500 shadow-lg shadow-forest-500/50 animate-pulse"
								: "bg-error shadow-lg shadow-error/50"
						}`}
					/>
					<span className="text-text-secondary text-xs font-medium uppercase tracking-wider">
						{isConnected ? "Connected" : "Disconnected"}
					</span>
				</div>
			</div>
		</div>
	);
}
