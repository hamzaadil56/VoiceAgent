import AnimatedCircle from "./AnimatedCircle";
import { useVoiceBotViewModel } from "../viewmodels/useVoiceBotViewModel";

export default function VoiceBot() {
	const {
		conversationHistory,
		effectiveState,
		isRecording,
		isPlaying,
		isConnected,
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
		<div className="glass-elevated rounded-3xl shadow-2xl p-10 border border-border/50">
			{/* Status and Circle */}
			<div className="flex flex-col items-center mb-10">
				<AnimatedCircle
					state={effectiveState}
					size={220}
					onClick={
						turnCount >= getMaxTurns()
							? undefined // Disable click when max turns reached
							: isRecording
							? handleStopRecording
							: effectiveState === "idle" ||
							  effectiveState === "connected"
							? handleStartRecording
							: undefined // Disable click during processing/speaking
					}
				/>
				<p className="mt-6 text-text-primary text-xl font-heading font-semibold tracking-tight">
					{getStateLabel()}
				</p>
				{processingTime !== null && (
					<div className="mt-3 flex items-center gap-2 px-4 py-2 glass rounded-full">
						<div className="w-1.5 h-1.5 rounded-full bg-accent-primary animate-pulse"></div>
						<p className="text-accent-secondary text-sm font-body font-medium">
							Processing: {processingTime}s
						</p>
					</div>
				)}
				{!isRecording &&
					!isPlaying &&
					(effectiveState === "idle" ||
						effectiveState === "connected") &&
					turnCount < getMaxTurns() && (
						<p className="mt-4 text-text-secondary text-sm font-body animate-fade-in">
							Tap the circle above to start talking
						</p>
					)}
				{isRecording && !isPlaying && (
					<div className="mt-4 flex items-center gap-2 px-4 py-2 glass rounded-full border border-success/30">
						<div className="w-2 h-2 rounded-full bg-success animate-pulse"></div>
						<p className="text-success text-sm font-body font-medium animate-pulse">
							Listening — Tap circle when finished
						</p>
					</div>
				)}
				{turnCount >= getMaxTurns() && (
					<div className="mt-4 px-5 py-3 glass rounded-xl border border-warning/40 bg-warning/5">
						<p className="text-warning text-sm font-body font-semibold text-center">
							Turn limit reached ({getMaxTurns()} turns). Refresh to continue.
						</p>
					</div>
				)}
				{turnCount > 0 && turnCount < getMaxTurns() && (
					<div className="mt-4 px-4 py-2 glass rounded-full">
						<p className="text-text-tertiary text-xs font-body font-medium tracking-wide uppercase">
							Turn {turnCount} of {getMaxTurns()}
						</p>
					</div>
				)}
				{error && (
					<div className="mt-4 px-5 py-3 glass rounded-xl border border-error/40 bg-error/5">
						<p className="text-error text-sm font-body">{error}</p>
					</div>
				)}
			</div>

			{/* Controls */}
			{/* <div className="flex justify-center gap-4 mb-8">
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
			</div> */}

			{/* Text Input Alternative */}
			{/* <form onSubmit={handleTextSubmitForm} className="mb-6">
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
			</form> */}

			{/* Conversation History */}
			{conversationHistory.length > 0 && (
				<div className="glass rounded-2xl p-6 max-h-80 overflow-y-auto border border-border/30">
					<h3 className="text-text-primary font-heading font-semibold mb-4 text-lg tracking-tight">
						Conversation
					</h3>
					<div className="space-y-3">
						{conversationHistory.map((msg, idx) => (
							<div
								key={idx}
								className={`p-4 rounded-xl border transition-all duration-300 animate-slide-up ${
									msg.role === "user"
										? "bg-accent-primary/10 border-accent-primary/30 text-text-primary"
										: "bg-accent-secondary/10 border-accent-secondary/30 text-text-primary"
								}`}
								style={{ animationDelay: `${idx * 0.1}s` }}
							>
								<span className="font-body font-semibold text-xs uppercase tracking-wider mb-1 block opacity-70">
									{msg.role === "user" ? "You" : "Agent"}
								</span>
								<p className="font-body text-sm leading-relaxed">{msg.text}</p>
							</div>
						))}
					</div>
				</div>
			)}

			{/* Connection Status */}
			<div className="mt-6 text-center">
				<div className="inline-flex items-center gap-2 px-4 py-2 glass rounded-full">
					<span
						className={`inline-block w-2.5 h-2.5 rounded-full ${
							isConnected 
								? "bg-success shadow-lg shadow-success/50 animate-pulse" 
								: "bg-error shadow-lg shadow-error/50"
						}`}
					/>
					<span className="text-text-secondary text-xs font-body font-medium uppercase tracking-wider">
						{isConnected ? "Connected" : "Disconnected"}
					</span>
				</div>
			</div>
		</div>
	);
}
