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
