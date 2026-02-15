/** Hook for managing consumer form session state */
import { useCallback, useState } from "react";
import { createSession, sendMessage } from "../api/consumerApi";
import type { ChatMessage } from "../../../shared/types/api";

export type SessionStatus = "idle" | "starting" | "active" | "sending" | "completed" | "error";

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

	const send = useCallback(
		async (text: string) => {
			if (!text.trim() || !sessionId || !sessionToken) return;

			setMessages((prev) => [...prev, { role: "user", content: text.trim(), timestamp: Date.now() }]);
			setStatus("sending");
			setError(null);

			try {
				const response = await sendMessage(sessionId, sessionToken, text.trim());
				setMessages((prev) => [
					...prev,
					{ role: "assistant", content: response.assistant_message, timestamp: Date.now() },
				]);
				setStatus(response.state === "completed" ? "completed" : "active");
			} catch (err) {
				setError(err instanceof Error ? err.message : "Failed to send message");
				setStatus("error");
			}
		},
		[sessionId, sessionToken],
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
