/** Chat message bubble component */
import type { ChatMessage } from "../../../shared/types/api";

interface MessageBubbleProps {
	message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
	const isBot = message.role === "assistant";

	return (
		<div className={`flex ${isBot ? "justify-start" : "justify-end"}`}>
			<div
				className={`max-w-[80%] px-4 py-3 rounded-2xl ${
					isBot
						? "bg-accent-secondary/10 text-text-primary rounded-bl-md"
						: "bg-accent-primary/15 text-text-primary rounded-br-md"
				}`}
			>
				<p className="text-[10px] uppercase tracking-widest opacity-40 mb-1 font-medium">
					{isBot ? "Bot" : "You"}
				</p>
				<p className="leading-relaxed whitespace-pre-wrap">{message.content}</p>
			</div>
		</div>
	);
}

/** Typing indicator dots */
export function TypingIndicator() {
	return (
		<div className="flex justify-start">
			<div className="bg-accent-secondary/10 px-4 py-3 rounded-2xl rounded-bl-md">
				<div className="flex gap-1.5">
					<span
						className="w-2 h-2 bg-text-tertiary/60 rounded-full animate-bounce"
						style={{ animationDelay: "0ms" }}
					/>
					<span
						className="w-2 h-2 bg-text-tertiary/60 rounded-full animate-bounce"
						style={{ animationDelay: "150ms" }}
					/>
					<span
						className="w-2 h-2 bg-text-tertiary/60 rounded-full animate-bounce"
						style={{ animationDelay: "300ms" }}
					/>
				</div>
			</div>
		</div>
	);
}
