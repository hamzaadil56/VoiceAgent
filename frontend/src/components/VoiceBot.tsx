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
		<div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8">
			{/* Status and Circle */}
			<div className="flex flex-col items-center mb-8">
				<AnimatedCircle
					state={effectiveState}
					size={200}
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
				<p className="mt-4 text-white text-lg font-semibold">
					{getStateLabel()}
				</p>
				{processingTime !== null && (
					<p className="mt-2 text-blue-300 text-sm">
						⚡ Processing time: {processingTime}s
					</p>
				)}
				{!isRecording &&
					!isPlaying &&
					(effectiveState === "idle" ||
						effectiveState === "connected") &&
					turnCount < getMaxTurns() && (
						<p className="mt-2 text-blue-300 text-sm">
							👆 Tap the circle above to start talking
						</p>
					)}
				{isRecording && !isPlaying && (
					<p className="mt-2 text-green-300 text-sm animate-pulse">
						✓ Listening - Tap circle or "Stop" when you finish
						speaking
					</p>
				)}
				{turnCount >= getMaxTurns() && (
					<p className="mt-2 text-yellow-300 text-sm font-semibold">
						⚠️ Turn limit reached ({getMaxTurns()} turns). Session
						stopped. Please refresh to continue.
					</p>
				)}
				{turnCount > 0 && turnCount < getMaxTurns() && (
					<p className="mt-2 text-white/60 text-sm">
						Turn {turnCount} of {getMaxTurns()}
					</p>
				)}
				{error && <p className="mt-2 text-red-300 text-sm">{error}</p>}
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
