/** Unified HTTP client for API communication */

const API_BASE = (
	import.meta.env.VITE_BACKEND_URL || ""
).replace(/\/$/, "");

const ADMIN_TOKEN_KEY = "agentic_admin_token";
const SESSION_TOKEN_KEY = "agentic_session_token";

// --- Token helpers ---

export function getAdminToken(): string | null {
	return localStorage.getItem(ADMIN_TOKEN_KEY);
}

export function setAdminToken(token: string) {
	localStorage.setItem(ADMIN_TOKEN_KEY, token);
}

export function clearAdminToken() {
	localStorage.removeItem(ADMIN_TOKEN_KEY);
}

export function getSessionToken(): string | null {
	return sessionStorage.getItem(SESSION_TOKEN_KEY);
}

export function setSessionToken(token: string) {
	sessionStorage.setItem(SESSION_TOKEN_KEY, token);
}

export function clearSessionToken() {
	sessionStorage.removeItem(SESSION_TOKEN_KEY);
}

// --- API Error ---

export class ApiError extends Error {
	constructor(
		public status: number,
		public code: string,
		message: string,
	) {
		super(message);
		this.name = "ApiError";
	}
}

// --- HTTP Client ---

async function request<T>(
	path: string,
	init: RequestInit = {},
	token?: string | null,
): Promise<T> {
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
		let code = "unknown_error";
		try {
			const body = await response.json();
			if (body?.detail) message = body.detail;
			if (body?.code) code = body.code;
		} catch {
			// ignore parse errors
		}
		throw new ApiError(response.status, code, message);
	}

	return response.json();
}

/** Admin-scoped API calls (auto-attaches admin token) */
export const adminApi = {
	get<T>(path: string): Promise<T> {
		return request<T>(`/v1${path}`, {}, getAdminToken());
	},
	post<T>(path: string, data?: unknown): Promise<T> {
		return request<T>(
			`/v1${path}`,
			{ method: "POST", body: data ? JSON.stringify(data) : undefined },
			getAdminToken(),
		);
	},
	patch<T>(path: string, data?: unknown): Promise<T> {
		return request<T>(
			`/v1${path}`,
			{ method: "PATCH", body: data ? JSON.stringify(data) : undefined },
			getAdminToken(),
		);
	},
};

/** Public-scoped API calls (uses session token) */
export const publicApi = {
	post<T>(path: string, data?: unknown, token?: string): Promise<T> {
		return request<T>(
			`/v1/public${path}`,
			{ method: "POST", body: data ? JSON.stringify(data) : undefined },
			token,
		);
	},
	get<T>(path: string, token?: string): Promise<T> {
		return request<T>(`/v1/public${path}`, {}, token);
	},
};
