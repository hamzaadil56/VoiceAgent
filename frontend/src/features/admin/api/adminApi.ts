/** Admin feature API functions */
import { adminApi } from "../../../shared/lib/httpClient";
import type {
	ExportResponse,
	FormCreatePayload,
	FormCreateResponse,
	FormGenerateResponse,
	FormSummary,
	PublishResponse,
	SubmissionsResponse,
} from "../../../shared/types/api";

export async function fetchForms(orgId: string) {
	return adminApi.get<{ forms: FormSummary[] }>(`/orgs/${orgId}/forms`);
}

export async function fetchForm(formId: string) {
	return adminApi.get<FormSummary>(`/forms/${formId}`);
}

/** Use AI to generate a form definition from a natural language prompt. */
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
	payload: Partial<Pick<FormSummary, "title" | "description" | "persona" | "mode" | "system_prompt">>,
) {
	return adminApi.patch<FormSummary>(`/forms/${formId}`, payload);
}

export async function publishForm(formId: string) {
	return adminApi.post<PublishResponse>(`/forms/${formId}/publish`);
}

export async function fetchSubmissions(formId: string) {
	return adminApi.get<SubmissionsResponse>(`/forms/${formId}/submissions`);
}

export async function exportCsv(formId: string) {
	return adminApi.post<ExportResponse>(`/forms/${formId}/exports/csv`);
}
