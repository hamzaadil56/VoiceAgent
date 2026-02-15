/** Chat interface for consumer form sessions */
import { type FormEvent, useEffect, useRef, useState } from "react";
import type { ChatMessage } from "../../../shared/types/api";
import type { SessionStatus } from "../hooks/useConsumerSession";
import { MessageBubble, TypingIndicator } from "./MessageBubble";

interface ChatInterfaceProps {
	messages: ChatMessage[];
	status: SessionStatus;
	error: string | null;
	onSend: (message: string) => void;
	onSwitchToVoice?: () => void;
}

export function ChatInterface({
	messages,
	status,
	error,
	onSend,
	onSwitchToVoice,
}: ChatInterfaceProps) {
	const [input, setInput] = useState("");
	const chatEndRef = useRef<HTMLDivElement>(null);
	const inputRef = useRef<HTMLInputElement>(null);

	// Auto scroll to bottom
	useEffect(() => {
		chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
	}, [messages, status]);

	// Auto focus input
	useEffect(() => {
		if (status === "active") {
			inputRef.current?.focus();
		}
	}, [status]);

	const handleSubmit = (e: FormEvent) => {
		e.preventDefault();
		if (!input.trim() || status === "sending") return;
		onSend(input.trim());
		setInput("");
	};

	const isCompleted = status === "completed";
	const isSending = status === "sending";

	return (
		<div
			className="glass-elevated rounded-2xl border border-border/40 overflow-hidden flex flex-col"
			style={{ height: "70vh", maxHeight: "600px" }}
		>
			{/* Messages Area */}
			<div className="flex-1 overflow-y-auto p-6 space-y-4">
				{messages.map((msg, i) => (
					<MessageBubble key={i} message={msg} />
				))}
				{isSending && <TypingIndicator />}
				{error && (
					<div className="text-center">
						<p className="text-sm text-error bg-error/10 px-4 py-2 rounded-xl inline-block" role="alert">
							{error}
						</p>
					</div>
				)}
				<div ref={chatEndRef} />
			</div>

			{/* Input Area */}
			{!isCompleted ? (
				<div className="border-t border-border/40 p-4">
					<form className="flex gap-3" onSubmit={handleSubmit}>
						<input
							ref={inputRef}
							value={input}
							onChange={(e) => setInput(e.target.value)}
							className="flex-1 px-4 py-3 glass rounded-xl border border-border text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-accent-primary"
							placeholder="Type your answer..."
							disabled={isSending}
							autoFocus
						/>
						<button
							type="submit"
							disabled={isSending || !input.trim()}
							className="px-5 py-3 rounded-xl bg-accent-primary text-bg-primary font-semibold hover:opacity-90 disabled:opacity-50"
						>
							Send
						</button>
						{onSwitchToVoice && (
							<button
								type="button"
								onClick={onSwitchToVoice}
								className="px-4 py-3 rounded-xl glass border border-border text-text-secondary hover:text-text-primary"
								title="Switch to voice mode"
							>
								<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
									<path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z" />
								</svg>
							</button>
						)}
					</form>
				</div>
			) : (
				<div className="border-t border-border/40 p-6 text-center">
					<div className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-success/10 text-success">
						<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
							<path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
						</svg>
						<span className="font-medium">Form completed! Thank you for your responses.</span>
					</div>
				</div>
			)}
		</div>
	);
}
