/** Consumer form page - chat and voice modes */
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

	const handleSwitchToVoice = () => {
		setActiveMode("voice");
	};

	const handleSwitchToChat = () => {
		setActiveMode("chat");
	};

	return (
		<div className="min-h-screen flex flex-col items-center justify-center relative z-10 px-4 py-8">
			<div className="w-full max-w-2xl">
				{/* Header */}
				<div className="text-center mb-6">
					<h1 className="text-2xl font-heading font-bold text-text-primary">
						Agentic Form
					</h1>
					{slug && (
						<p className="text-sm text-text-tertiary mt-1">/{slug}</p>
					)}
				</div>

				{!session.isStarted ? (
					/* Session start screen */
					<div className="glass-elevated rounded-2xl border border-border/40 p-8 text-center space-y-6">
						<div>
							<h2 className="text-xl font-heading text-text-primary mb-2">
								Ready to begin?
							</h2>
							<p className="text-text-secondary">
								Answer a few questions through a conversational experience.
							</p>
						</div>

						<div className="flex justify-center gap-3">
							<button
								onClick={() => setChannel("chat")}
								className={`px-5 py-3 rounded-xl font-medium ${
									channel === "chat"
										? "bg-accent-primary text-bg-primary"
										: "glass border border-border text-text-secondary hover:text-text-primary"
								}`}
							>
								<span className="flex items-center gap-2">
									<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
										<path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H8.25m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H12m4.125 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 0 1-2.555-.337A5.972 5.972 0 0 1 5.41 20.97a5.969 5.969 0 0 1-.474-.065 4.48 4.48 0 0 0 .978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25Z" />
									</svg>
									Chat
								</span>
							</button>
							<button
								onClick={() => setChannel("voice")}
								className={`px-5 py-3 rounded-xl font-medium ${
									channel === "voice"
										? "bg-accent-primary text-bg-primary"
										: "glass border border-border text-text-secondary hover:text-text-primary"
								}`}
							>
								<span className="flex items-center gap-2">
									<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
										<path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z" />
									</svg>
									Voice
								</span>
							</button>
						</div>

						<button
							onClick={handleStart}
							disabled={session.status === "starting"}
							className="px-8 py-3.5 rounded-xl bg-accent-primary text-bg-primary font-semibold text-lg hover:opacity-90 disabled:opacity-50"
						>
							{session.status === "starting" ? (
								<span className="flex items-center gap-2">
									<span className="w-4 h-4 border-2 border-bg-primary border-t-transparent rounded-full animate-spin" />
									Starting...
								</span>
							) : (
								"Start Form"
							)}
						</button>

						{session.error && (
							<p className="text-error text-sm" role="alert">{session.error}</p>
						)}
					</div>
				) : activeMode === "voice" ? (
					/* Voice interface */
					<VoiceInterface
						sessionId={session.sessionId}
						sessionToken={session.sessionToken}
						onSwitchToChat={handleSwitchToChat}
					/>
				) : (
					/* Chat interface */
					<ChatInterface
						messages={session.messages}
						status={session.status}
						error={session.error}
						onSend={session.send}
						onSwitchToVoice={channel === "voice" || channel === "chat" ? handleSwitchToVoice : undefined}
					/>
				)}
			</div>
		</div>
	);
}
