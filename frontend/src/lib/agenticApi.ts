const API_BASE = (import.meta.env.VITE_BACKEND_URL || "http://localhost:8000").replace(/\/$/, "");

const ADMIN_TOKEN_KEY = "agentic_admin_token";

export type GraphNodeIn = {
	key: string;
	prompt: string;
	node_type?: "question" | "statement";
	required?: boolean;
	validation?: Record<string, unknown>;
};

export type GraphEdgeIn = {
	from_key: string;
	to_key?: string | null;
	condition?: Record<string, unknown> | null;
};

export function getAdminToken(): string | null {
	return localStorage.getItem(ADMIN_TOKEN_KEY);
}

export function setAdminToken(token: string) {
	localStorage.setItem(ADMIN_TOKEN_KEY, token);
}

export function clearAdminToken() {
	localStorage.removeItem(ADMIN_TOKEN_KEY);
}

async function request<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
	const headers: Record<string, string> = {
		"Content-Type": "application/json",
		...(init.headers as Record<string, string>),
	};
	if (token) {
		headers.Authorization = `Bearer ${token}`;
	}

	const response = await fetch(`${API_BASE}${path}`, { ...init, headers });
	if (!response.ok) {
		let message = `Request failed (${response.status})`;
		try {
			const body = await response.json();
			if (body?.detail) message = body.detail;
		} catch {
			// ignore
		}
		throw new Error(message);
	}
	return response.json();
}

export async function loginAdmin(email: string, password: string) {
	return request<{ access_token: string }>("/v1/auth/login", {
		method: "POST",
		body: JSON.stringify({ email, password }),
	});
}

export async function fetchMe(token: string) {
	return request<{ id: string; email: string; memberships: { org_id: string; role: string }[] }>("/v1/auth/me", {}, token);
}

export async function createForm(token: string, orgId: string, payload: {
	title: string;
	description: string;
	slug: string;
	mode: "chat" | "voice" | "chat_voice";
	persona: string;
	start_node_key: string;
	graph_nodes: GraphNodeIn[];
	graph_edges: GraphEdgeIn[];
}) {
	return request<{ id: string; slug: string; version_id: string; status: string }>(`/v1/orgs/${orgId}/forms`, {
		method: "POST",
		body: JSON.stringify(payload),
	}, token);
}

export async function publishForm(token: string, formId: string) {
	return request<{ form_id: string; published_version_id: string; status: string }>(`/v1/forms/${formId}/publish`, {
		method: "POST",
	}, token);
}

export async function fetchSubmissions(token: string, formId: string) {
	return request<{ form_id: string; total: number; rows: Array<{ submission_id: string; answers: Record<string, string> }> }>(`/v1/forms/${formId}/submissions`, {}, token);
}

export async function exportCsv(token: string, formId: string) {
	return request<{ export_id: string; status: string; row_count: number; file_path?: string }>(`/v1/forms/${formId}/exports/csv`, {
		method: "POST",
	}, token);
}

export async function createPublicSession(slug: string, channel: "chat" | "voice") {
	return request<{ session_id: string; session_token: string; assistant_message: string }>(`/v1/public/f/${slug}/sessions`, {
		method: "POST",
		body: JSON.stringify({ channel, locale: "en", metadata: {} }),
	});
}

export async function sendPublicMessage(sessionId: string, sessionToken: string, message: string) {
	return request<{ assistant_message: string; state: string; accepted: boolean }>(`/v1/public/sessions/${sessionId}/message`, {
		method: "POST",
		headers: { Authorization: `Bearer ${sessionToken}` },
		body: JSON.stringify({ message }),
	});
}
