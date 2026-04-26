/** Hook for managing consumer form session state with streaming support */
import { useCallback, useRef, useState } from "react";
import { createSession, sendMessage, streamMessage } from "../api/consumerApi";
import type { ChatMessage } from "../../../shared/types/api";

export type SessionStatus = "idle" | "starting" | "active" | "sending" | "streaming" | "completed" | "abandoned" | "error";

function statusFromState(state: string): SessionStatus {
	if (state === "completed") return "completed";
	if (state === "abandoned") return "abandoned";
	return "active";
}

interface UseConsumerSessionReturn {
	sessionId: string;
	sessionToken: string;
	messages: ChatMessage[];
	status: SessionStatus;
	error: string | null;
	isStarted: boolean;
	startSession: (slug: string, channel: "chat" | "voice") => Promise<void>;
	send: (message: string) => Promise<void>;
}

export function useConsumerSession(): UseConsumerSessionReturn {
	const [sessionId, setSessionId] = useState("");
	const [sessionToken, setSessionToken] = useState("");
	const [messages, setMessages] = useState<ChatMessage[]>([]);
	const [status, setStatus] = useState<SessionStatus>("idle");
	const [error, setError] = useState<string | null>(null);
	const streamingIndexRef = useRef<number>(-1);

	const isStarted = Boolean(sessionId && sessionToken);

	const startSession = useCallback(async (slug: string, channel: "chat" | "voice") => {
		setStatus("starting");
		setError(null);
		try {
			const response = await createSession(slug, channel);
			setSessionId(response.session_id);
			setSessionToken(response.session_token);
			setMessages([
				{ role: "assistant", content: response.assistant_message, timestamp: Date.now() },
			]);
			setStatus("active");
		} catch (err) {
			setError(err instanceof Error ? err.message : "Failed to start session");
			setStatus("error");
		}
	}, []);

	const sendNonStreaming = useCallback(
		async (text: string) => {
			setMessages((prev) => [...prev, { role: "user", content: text, timestamp: Date.now() }]);
			setStatus("sending");
			setError(null);
			try {
				const response = await sendMessage(sessionId, sessionToken, text);
				setMessages((prev) => [
					...prev,
					{ role: "assistant", content: response.assistant_message, timestamp: Date.now() },
				]);
				setStatus(statusFromState(response.state));
			} catch (err) {
				setError(err instanceof Error ? err.message : "Failed to send message");
				setStatus("error");
			}
		},
		[sessionId, sessionToken],
	);

	const send = useCallback(
		async (text: string) => {
			if (!text.trim() || !sessionId || !sessionToken) return;
			const trimmed = text.trim();

			const userMsg: ChatMessage = { role: "user", content: trimmed, timestamp: Date.now() };
			const placeholderMsg: ChatMessage = { role: "assistant", content: "", timestamp: Date.now() };

			setMessages((prev) => {
				const next = [...prev, userMsg, placeholderMsg];
				streamingIndexRef.current = next.length - 1;
				return next;
			});
			setStatus("streaming");
			setError(null);

			let streamFailed = false;

			try {
				await streamMessage(
					sessionId,
					sessionToken,
					trimmed,
					(delta) => {
						setMessages((prev) => {
							const updated = [...prev];
							const idx = streamingIndexRef.current;
							if (idx >= 0 && idx < updated.length) {
								updated[idx] = {
									...updated[idx],
									content: updated[idx].content + delta,
								};
							}
							return updated;
						});
					},
					(doneData) => {
						streamingIndexRef.current = -1;
						setStatus(statusFromState(doneData.state));
					},
					(errMsg) => {
						streamingIndexRef.current = -1;
						if (errMsg.includes("Not Found") || errMsg.includes("404")) {
							streamFailed = true;
						} else {
							setError(errMsg);
							setStatus("error");
						}
					},
				);
			} catch {
				streamFailed = true;
			}

			if (streamFailed) {
				streamingIndexRef.current = -1;
				setMessages((prev) => prev.slice(0, -2));
				await sendNonStreaming(trimmed);
			}
		},
		[sessionId, sessionToken, sendNonStreaming],
	);

	return {
		sessionId,
		sessionToken,
		messages,
		status,
		error,
		isStarted,
		startSession,
		send,
	};
}
