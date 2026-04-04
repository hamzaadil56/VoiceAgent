/** Shared API types for Agentic Forms Platform */

// --- Auth ---
export interface AdminUser {
	id: string;
	email: string;
	full_name: string;
	memberships: OrgMembership[];
}

export interface OrgMembership {
	org_id: string;
	role: string;
}

export interface TokenResponse {
	access_token: string;
	token_type: string;
}

// --- Form Fields (agentic) ---
export interface FormField {
	name: string;
	type: "text" | "email" | "number" | "phone" | "url" | "date" | "select" | "boolean";
	required: boolean;
	description: string;
}

// --- Form Generation (AI-powered) ---
export interface FormGenerateRequest {
	prompt: string;
}

export interface FormGenerateResponse {
	title: string;
	description: string;
	system_prompt: string;
	fields: FormField[];
}

// --- Form CRUD ---
export interface FormCreatePayload {
	title: string;
	description: string;
	slug: string;
	mode: "chat" | "voice" | "chat_voice";
	persona: string;
	system_prompt: string;
	fields: FormField[];
}

export interface FormCreateResponse {
	id: string;
	org_id: string;
	slug: string;
	status: string;
}

export interface FormSummary {
	id: string;
	org_id: string;
	title: string;
	description: string;
	slug: string;
	mode: string;
	persona: string;
	status: string;
	system_prompt: string;
	fields_schema: FormField[];
	published_version_id: string | null;
	created_at: string;
	updated_at: string;
}

export interface PublishResponse {
	form_id: string;
	status: string;
}

// --- Submissions ---
export interface SubmissionRow {
	submission_id: string;
	session_id: string;
	completed_at: string;
	answers: Record<string, string>;
}

export interface SubmissionsResponse {
	form_id: string;
	total: number;
	rows: SubmissionRow[];
}

// --- Org dashboard analytics ---
export interface DashboardDailyPoint {
	date: string;
	count: number;
}

export interface DashboardFormAggregate {
	form_id: string;
	title: string;
	slug: string;
	status: string;
	mode: string;
	submission_count: number;
}

export interface DashboardRecentSubmission {
	submission_id: string;
	form_id: string;
	form_title: string;
	completed_at: string;
}

export interface OrgDashboardResponse {
	total_submissions: number;
	total_sessions: number;
	completion_rate_pct: number;
	published_forms: number;
	draft_forms: number;
	submissions_last_7d: number;
	submissions_prev_7d: number;
	submissions_trend_pct: number | null;
	completion_rate_trend_pct: number | null;
	avg_completion_seconds: number | null;
	submissions_by_channel: Record<string, number>;
	daily_submissions: DashboardDailyPoint[];
	forms: DashboardFormAggregate[];
	recent_submissions: DashboardRecentSubmission[];
}

export interface ExportResponse {
	export_id: string;
	status: string;
	row_count: number;
	file_path?: string;
}

// --- Public Consumer ---
export interface PublicSessionResponse {
	session_id: string;
	session_token: string;
	state: string;
	assistant_message: string;
}

export interface PublicMessageResponse {
	session_id: string;
	state: string;
	accepted: boolean;
	assistant_message: string;
}

export interface ChatMessage {
	role: "assistant" | "user";
	content: string;
	timestamp?: number;
}
