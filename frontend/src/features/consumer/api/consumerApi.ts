/** Consumer-facing API functions */
import { publicApi } from "../../../shared/lib/httpClient";
import type { PublicMessageResponse, PublicSessionResponse } from "../../../shared/types/api";

export async function createSession(slug: string, channel: "chat" | "voice") {
	return publicApi.post<PublicSessionResponse>(`/f/${slug}/sessions`, {
		channel,
		locale: "en",
		metadata: {},
	});
}

export async function sendMessage(
	sessionId: string,
	sessionToken: string,
	message: string,
) {
	return publicApi.post<PublicMessageResponse>(
		`/sessions/${sessionId}/message`,
		{ message },
		sessionToken,
	);
}

export async function getMessages(sessionId: string, sessionToken: string) {
	return publicApi.get<{
		session_id: string;
		messages: Array<{ id: string; role: string; content: string; created_at: string }>;
	}>(`/sessions/${sessionId}/messages`, sessionToken);
}

/**
 * Stream the agent response token-by-token via SSE.
 * Calls the onDelta callback for each token and onDone when complete.
 */
export async function streamMessage(
	sessionId: string,
	sessionToken: string,
	message: string,
	onDelta: (token: string) => void,
	onDone: (data: { state: string; accepted: boolean; assistant_message: string }) => void,
	onError?: (error: string) => void,
): Promise<void> {
	const response = await fetch(
		`/v1/public/sessions/${sessionId}/message/stream`,
		{
			method: "POST",
			headers: {
				"Content-Type": "application/json",
				...(sessionToken ? { Authorization: `Bearer ${sessionToken}` } : {}),
			},
			body: JSON.stringify({ message }),
		},
	);

	if (!response.ok) {
		const errText = await response.text().catch(() => "Stream request failed");
		onError?.(errText);
		return;
	}

	const reader = response.body?.getReader();
	if (!reader) {
		onError?.("No response body");
		return;
	}

	const decoder = new TextDecoder();
	let buffer = "";

	while (true) {
		const { done, value } = await reader.read();
		if (done) break;

		buffer += decoder.decode(value, { stream: true });

		const lines = buffer.split("\n");
		buffer = lines.pop() || "";

		for (const line of lines) {
			const trimmed = line.trim();
			if (!trimmed.startsWith("data: ")) continue;

			try {
				const payload = JSON.parse(trimmed.slice(6));
				if (payload.type === "delta" && payload.content) {
					onDelta(payload.content);
				} else if (payload.type === "done") {
					onDone(payload);
				} else if (payload.type === "error") {
					onError?.(payload.content || "Stream error");
				}
			} catch {
				// ignore malformed SSE lines
			}
		}
	}
}
