import type { ChatMessage } from "../../../shared/types/api";

interface MessageBubbleProps {
	message: ChatMessage;
	isStreaming?: boolean;
}

export function MessageBubble({ message, isStreaming }: MessageBubbleProps) {
	const isBot = message.role === "assistant";

	if (isBot) {
		return (
			<div className="flex gap-2 items-end max-w-[85%] self-start animate-bubble-left">
				{/* Fired clay agent avatar */}
				<div className="w-7 h-7 rounded-full flex-shrink-0 grid place-items-center text-white text-[11px] font-medium bg-clay-500">
					AF
				</div>
				<div className="msg-bot-bubble px-3.5 py-2.5">
					<p className={`whitespace-pre-wrap${isStreaming ? " streaming-cursor" : ""}`}>
						{message.content}
					</p>
				</div>
			</div>
		);
	}

	return (
		<div className="flex justify-end max-w-[85%] self-end animate-bubble-right">
			<div className="msg-user-bubble px-3.5 py-2.5">
				<p className="whitespace-pre-wrap">{message.content}</p>
			</div>
		</div>
	);
}

export function TypingIndicator() {
	return (
		<div className="flex gap-2 items-end max-w-[85%] self-start animate-bubble-left">
			<div className="w-7 h-7 rounded-full flex-shrink-0 grid place-items-center text-white text-[11px] font-medium bg-clay-500">
				AF
			</div>
			<div
				className="flex gap-[5px] items-center px-3.5 py-3 bg-clay-100 rounded-lg"
				style={{ borderBottomLeftRadius: "var(--radius-xs)" }}
			>
				<span
					className="w-[7px] h-[7px] rounded-full bg-clay-300"
					style={{ animation: "typing-bounce 1.5s infinite ease-in-out" }}
				/>
				<span
					className="w-[7px] h-[7px] rounded-full bg-clay-300"
					style={{ animation: "typing-bounce 1.5s infinite ease-in-out 0.18s" }}
				/>
				<span
					className="w-[7px] h-[7px] rounded-full bg-clay-300"
					style={{ animation: "typing-bounce 1.5s infinite ease-in-out 0.36s" }}
				/>
			</div>
		</div>
	);
}
