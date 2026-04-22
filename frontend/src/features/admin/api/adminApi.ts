/** Admin feature API functions */
import { adminApi } from "../../../shared/lib/httpClient";
import type {
	ApiKeyItem,
	BillingResponse,
	ExportResponse,
	FormAnalytics,
	FormCreatePayload,
	FormCreateResponse,
	FormGenerateResponse,
	FormSummary,
	FormTemplate,
	InvitationItem,
	PublishResponse,
	SubmissionsResponse,
	TeamMember,
	WebhookConfig,
} from "../../../shared/types/api";

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
		> & { branding?: Record<string, string>; fields?: FormSummary["fields_schema"] }
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

export async function exportCsv(formId: string) {
	return adminApi.post<ExportResponse>(`/forms/${formId}/exports/csv`);
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
