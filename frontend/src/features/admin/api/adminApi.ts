/** Admin feature API functions */
import { adminApi, getAdminToken, ApiError } from "../../../shared/lib/httpClient";
import type {
	ApiKeyItem,
	BillingResponse,
	FormAIInsightsResponse,
	FormAnalytics,
	FormCreatePayload,
	FormCreateResponse,
	FormBranding,
	FormFieldDistributionsResponse,
	FormGenerateResponse,
	FormSummary,
	FormTemplate,
	InvitationItem,
	PublishResponse,
	SubmissionsResponse,
	TeamMember,
	WebhookConfig,
} from "../../../shared/types/api";

const API_BASE = (import.meta.env.VITE_BACKEND_URL || "").replace(/\/$/, "");

export async function fetchForms(orgId: string) {
	return adminApi.get<{ forms: FormSummary[] }>(`/orgs/${orgId}/forms`);
}

export async function fetchForm(formId: string) {
	return adminApi.get<FormSummary>(`/forms/${formId}`);
}

export async function generateForm(orgId: string, prompt: string) {
	return adminApi.post<FormGenerateResponse>(`/orgs/${orgId}/forms/generate`, {
		prompt,
	});
}

export async function createForm(orgId: string, payload: FormCreatePayload) {
	return adminApi.post<FormCreateResponse>(`/orgs/${orgId}/forms`, payload);
}

export async function updateForm(
	formId: string,
	payload: Partial<
		Pick<
			FormSummary,
			| "title"
			| "description"
			| "slug"
			| "persona"
			| "mode"
			| "system_prompt"
			| "welcome_message"
			| "completion_message"
			| "locale"
		> & { branding?: FormBranding; fields?: FormSummary["fields_schema"] }
	>,
) {
	return adminApi.patch<FormSummary>(`/forms/${formId}`, payload);
}

export async function publishForm(formId: string) {
	return adminApi.post<PublishResponse>(`/forms/${formId}/publish`);
}

export async function unpublishForm(formId: string) {
	return adminApi.post<PublishResponse>(`/forms/${formId}/unpublish`);
}

export async function duplicateForm(formId: string) {
	return adminApi.post<FormCreateResponse>(`/forms/${formId}/duplicate`);
}

export async function fetchSubmissions(formId: string) {
	return adminApi.get<SubmissionsResponse>(`/forms/${formId}/submissions`);
}

export async function exportCsv(formId: string): Promise<void> {
	const token = getAdminToken();
	const response = await fetch(`${API_BASE}/v1/forms/${formId}/exports/csv`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			...(token ? { Authorization: `Bearer ${token}` } : {}),
		},
	});
	if (!response.ok) {
		let message = `Export failed (${response.status})`;
		let code = "unknown_error";
		try {
			const body = await response.json();
			if (body?.detail) message = body.detail;
			if (body?.code) code = body.code;
		} catch { /* ignore */ }
		throw new ApiError(response.status, code, message);
	}
	const blob = await response.blob();
	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = `form_${formId}_submissions.csv`;
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
	URL.revokeObjectURL(url);
}

// Templates
export async function fetchTemplates() {
	return adminApi.get<FormTemplate[]>("/templates");
}

export async function fetchTemplate(templateId: string) {
	return adminApi.get<FormTemplate>(`/templates/${templateId}`);
}

// Analytics
export async function fetchFormAnalytics(formId: string) {
	return adminApi.get<FormAnalytics>(`/forms/${formId}/analytics`);
}

// Insights
export async function fetchFieldDistributions(formId: string) {
	return adminApi.get<FormFieldDistributionsResponse>(`/forms/${formId}/insights/distributions`);
}

export async function generateAIInsights(formId: string) {
	return adminApi.post<FormAIInsightsResponse>(`/forms/${formId}/insights/generate`);
}

// Webhooks
export async function fetchWebhooks(formId: string) {
	return adminApi.get<WebhookConfig[]>(`/forms/${formId}/webhooks`);
}

export async function createWebhook(
	formId: string,
	payload: { url: string; events: string[] },
) {
	return adminApi.post<WebhookConfig>(`/forms/${formId}/webhooks`, payload);
}

export async function deleteWebhook(webhookId: string) {
	return adminApi.post(`/webhooks/${webhookId}/delete`);
}

// Team
export async function fetchMembers(orgId: string) {
	return adminApi.get<TeamMember[]>(`/orgs/${orgId}/members`);
}

export async function inviteMember(
	orgId: string,
	payload: { email: string; role: string },
) {
	return adminApi.post<InvitationItem>(
		`/orgs/${orgId}/invitations`,
		payload,
	);
}

export async function fetchInvitations(orgId: string) {
	return adminApi.get<InvitationItem[]>(`/orgs/${orgId}/invitations`);
}

// Billing
export async function fetchBilling(orgId: string) {
	return adminApi.get<BillingResponse>(`/orgs/${orgId}/billing`);
}

// API Keys
export async function fetchApiKeys(orgId: string) {
	return adminApi.get<ApiKeyItem[]>(`/orgs/${orgId}/api-keys`);
}

export async function createApiKey(
	orgId: string,
	payload: { name: string },
) {
	return adminApi.post<ApiKeyItem & { key: string }>(
		`/orgs/${orgId}/api-keys`,
		payload,
	);
}
