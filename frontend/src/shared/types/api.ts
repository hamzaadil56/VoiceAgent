/** Shared API types for Agentic Forms Platform */

// --- Auth ---
export interface AdminUser {
	id: string;
	email: string;
	full_name: string;
	memberships: OrgMembership[];
	plan: string;
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
	type:
		| "text"
		| "email"
		| "number"
		| "phone"
		| "url"
		| "date"
		| "select"
		| "boolean"
		| "file"
		| "payment";
	required: boolean;
	description: string;
	conditions?: FieldCondition[];
}

export interface FieldCondition {
	field_key: string;
	operator: "equals" | "not_equals" | "contains" | "greater_than" | "less_than";
	value: string;
}

// --- Form Branding ---
export interface FormBranding {
	logo_url: string;
	primary_color: string;
	accent_color: string;
	font: string;
	background_color: string;
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
	branding?: FormBranding;
	locale?: string;
	welcome_message?: string;
	completion_message?: string;
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
	branding: Record<string, string>;
	locale: string;
	welcome_message: string;
	completion_message: string;
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

// --- Templates ---
export interface FormTemplate {
	id: string;
	title: string;
	description: string;
	category: string;
	fields: FormField[];
	system_prompt: string;
	persona: string;
	mode: string;
}

// --- Analytics ---
export interface DropoffStep {
	field_key: string;
	field_name: string;
	sessions_reached: number;
	sessions_answered: number;
	dropoff_pct: number;
}

export interface FormAnalytics {
	form_id: string;
	total_sessions: number;
	total_submissions: number;
	completion_rate_pct: number;
	avg_completion_seconds: number | null;
	channel_breakdown: Record<string, number>;
	dropoff_funnel: DropoffStep[];
	sentiment_score: number | null;
}

// --- Billing ---
export interface PlanInfo {
	plan: string;
	responses_limit: number;
	forms_limit: number;
	voice_minutes_limit: number;
	seats_limit: number;
}

export interface UsageSummary {
	responses_used: number;
	responses_limit: number;
	voice_minutes_used: number;
	voice_minutes_limit: number;
	forms_used: number;
	forms_limit: number;
	seats_used: number;
	seats_limit: number;
	plan: string;
}

export interface BillingResponse {
	plan: PlanInfo;
	usage: UsageSummary;
	stripe_customer_id: string | null;
}

// --- Webhooks ---
export interface WebhookConfig {
	id: string;
	url: string;
	events: string[];
	is_active: boolean;
	created_at: string;
}

// --- Team ---
export interface TeamMember {
	id: string;
	user_id: string;
	email: string;
	full_name: string;
	role: string;
}

export interface InvitationItem {
	id: string;
	email: string;
	role: string;
	status: string;
}

// --- API Keys ---
export interface ApiKeyItem {
	id: string;
	name: string;
	prefix: string;
	is_active: boolean;
	last_used_at: string | null;
	created_at: string;
}
