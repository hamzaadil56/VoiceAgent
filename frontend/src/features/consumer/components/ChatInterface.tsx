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
	const inputRef = useRef<HTMLTextAreaElement>(null);

	useEffect(() => {
		chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
	}, [messages, status]);

	useEffect(() => {
		if (status === "active") {
			inputRef.current?.focus();
		}
	}, [status]);

	const handleSubmit = (e: FormEvent) => {
		e.preventDefault();
		if (!input.trim() || status === "sending" || status === "streaming") return;
		onSend(input.trim());
		setInput("");
	};

	const handleKeyDown = (e: React.KeyboardEvent) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();
			handleSubmit(e);
		}
	};

	const isCompleted = status === "completed";
	const isAbandoned = status === "abandoned";
	const isClosed = isCompleted || isAbandoned;
	const isBusy = status === "sending" || status === "streaming";
	const isStreaming = status === "streaming";

	return (
		<div
			className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 overflow-hidden flex flex-col shadow-md"
			style={{ height: "75vh", maxHeight: "680px" }}
		>
			{/* Messages */}
			<div className="flex-1 overflow-y-auto px-5 py-5 flex flex-col gap-4">
				{messages.map((msg, i) => (
					<MessageBubble
						key={i}
						message={msg}
						isStreaming={isStreaming && i === messages.length - 1 && msg.role === "assistant"}
					/>
				))}
				{status === "sending" && <TypingIndicator />}
				{error && (
					<div className="text-center">
						<p
							className="text-[13px] px-4 py-2 rounded-md inline-block"
							style={{ color: "var(--color-error)", background: "var(--error-bg)" }}
							role="alert"
						>
							{error}
						</p>
					</div>
				)}
				<div ref={chatEndRef} />
			</div>

			{/* Input area */}
			{!isClosed ? (
				<div className="px-5 pb-6 pt-3" style={{ background: "linear-gradient(to top, var(--stone-50) 75%, transparent)" }}>
					<form
						onSubmit={handleSubmit}
						className="flex items-end gap-2 rounded-full px-4 py-2.5 bg-bg-base border-[0.5px] border-stone-200 shadow-sm transition-all focus-within:border-forest-500 focus-within:shadow-forest-ring"
					>
						<textarea
							ref={inputRef}
							value={input}
							onChange={(e) => setInput(e.target.value)}
							onKeyDown={handleKeyDown}
							className="flex-1 border-none outline-none text-[14px] text-text-primary bg-transparent resize-none max-h-[120px] leading-normal placeholder:text-text-tertiary"
							placeholder="Or type your answer..."
							disabled={isBusy}
							rows={1}
							autoFocus
						/>
						{/* Send button */}
						<button
							type="submit"
							disabled={isBusy || !input.trim()}
							className="w-[36px] h-[36px] rounded-full grid place-items-center flex-shrink-0 text-white transition-all duration-150 hover:opacity-90 active:scale-[0.94] disabled:cursor-not-allowed"
							style={{
								background: (!isBusy && input.trim()) ? "var(--forest-500)" : "var(--stone-200)",
								color: (!isBusy && input.trim()) ? "white" : "var(--stone-400)",
							}}
						>
							<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
								<path strokeLinecap="round" strokeLinejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
							</svg>
						</button>
						{onSwitchToVoice && (
							<button
								type="button"
								onClick={onSwitchToVoice}
								className="w-[36px] h-[36px] rounded-full border-[0.5px] border-stone-200 grid place-items-center flex-shrink-0 text-text-tertiary hover:text-sage-500 hover:border-sage-300 transition-all duration-150"
								title="Switch to voice mode"
							>
								<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
									<path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z" />
								</svg>
							</button>
						)}
					</form>
				</div>
			) : (
				<div className="border-t border-stone-100 p-6 text-center">
					{isCompleted ? (
						<div className="inline-flex items-center gap-2 px-4 py-2 rounded-md text-[13px] font-medium bg-forest-100 text-forest-600">
							<svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
								<path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
							</svg>
							Form completed! Thank you for your responses.
						</div>
					) : (
						<div className="inline-flex items-center gap-2 px-4 py-2 rounded-md text-[13px] font-medium bg-stone-100 text-text-secondary">
							Conversation ended. You can come back anytime.
						</div>
					)}
				</div>
			)}
		</div>
	);
}
