import { useState } from "react";
import { useParams } from "react-router-dom";
import { useConsumerSession } from "../hooks/useConsumerSession";
import { ChatInterface } from "../components/ChatInterface";
import { VoiceInterface } from "../components/VoiceInterface";

export default function FormPage() {
	const { slug } = useParams<{ slug: string }>();
	const session = useConsumerSession();
	const [channel, setChannel] = useState<"chat" | "voice">("chat");
	const [activeMode, setActiveMode] = useState<"chat" | "voice">("chat");

	const handleStart = () => {
		if (!slug) return;
		setActiveMode(channel);
		session.startSession(slug, channel);
	};

	const handleSwitchToVoice = () => setActiveMode("voice");
	const handleSwitchToChat = () => setActiveMode("chat");

	return (
		<div className="consumer-runtime min-h-screen flex flex-col items-center px-4 py-8">
			{/* Header */}
			<div className="w-full max-w-[640px] px-2 pb-4">
				<div className="flex items-center gap-2 mb-2">
					<span className="w-2 h-2 rounded-full bg-forest-500 flex-shrink-0" />
					<span className="text-[11px] text-text-tertiary font-medium uppercase tracking-widest">
						AgentForms
					</span>
				</div>
				<h1 className="font-heading font-semibold text-[28px] text-text-primary leading-tight">
					{slug ? slug.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()) : "Agentic Form"}
				</h1>
				{slug && (
					<p className="text-[15px] text-text-secondary mt-1 leading-relaxed">
						Answer a few questions through a conversational experience.
					</p>
				)}
			</div>

			<div className="w-full max-w-[640px] flex-1 flex flex-col">
				{!session.isStarted ? (
					/* Start screen */
					<div className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 p-8 text-center space-y-6 animate-fade-up shadow-md">
						<div>
							<h2 className="font-heading font-semibold text-[22px] text-text-primary mb-2">
								Ready to begin?
							</h2>
							<p className="text-[15px] text-text-secondary leading-relaxed">
								Choose how you'd like to interact.
							</p>
						</div>

						{/* Channel selector */}
						<div className="flex justify-center gap-3">
							<button
								onClick={() => setChannel("chat")}
								className={`px-5 py-3 rounded-full font-medium text-[13px] transition-all duration-150 ${
									channel === "chat"
										? "bg-clay-500 text-white shadow-clay"
										: "bg-bg-base border-[0.5px] border-stone-200 text-text-primary hover:border-stone-300"
								}`}
							>
								<span className="flex items-center gap-2">
									<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
										<path strokeLinecap="round" strokeLinejoin="round" d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
									</svg>
									Chat
								</span>
							</button>
							<button
								onClick={() => setChannel("voice")}
								className={`px-5 py-3 rounded-full font-medium text-[13px] transition-all duration-150 ${
									channel === "voice"
										? "bg-sage-500 text-white shadow-sage"
										: "bg-bg-base border-[0.5px] border-stone-200 text-text-primary hover:border-stone-300"
								}`}
							>
								<span className="flex items-center gap-2">
									<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
										<path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z" />
									</svg>
									Voice
								</span>
							</button>
						</div>

						{/* Start button */}
						<button
							onClick={handleStart}
							disabled={session.status === "starting"}
							className="px-8 py-[9px] rounded-md font-medium text-[15px] text-white bg-forest-500 hover:bg-forest-600 transition-all duration-150 disabled:opacity-50 shadow-forest"
						>
							{session.status === "starting" ? (
								<span className="flex items-center gap-2">
									<span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
									Starting...
								</span>
							) : (
								"Start →"
							)}
						</button>

						{session.error && (
							<p className="text-[13px] text-error" role="alert">
								{session.error}
							</p>
						)}
					</div>
				) : activeMode === "voice" ? (
					<VoiceInterface
						sessionId={session.sessionId}
						sessionToken={session.sessionToken}
						onSwitchToChat={handleSwitchToChat}
					/>
				) : (
					<ChatInterface
						messages={session.messages}
						status={session.status}
						error={session.error}
						onSend={session.send}
						onSwitchToVoice={handleSwitchToVoice}
					/>
				)}
			</div>
		</div>
	);
}
