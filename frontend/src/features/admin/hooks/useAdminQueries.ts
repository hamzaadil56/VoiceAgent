/** TanStack Query hooks for admin data fetching. */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
	createForm,
	duplicateForm,
	exportCsv,
	fetchBilling,
	fetchForm,
	fetchFormAnalytics,
	fetchForms,
	fetchMembers,
	fetchSubmissions,
	fetchTemplates,
	generateForm,
	publishForm,
	unpublishForm,
	updateForm,
} from "../api/adminApi";
import { adminApi } from "../../../shared/lib/httpClient";
import type {
	FormCreatePayload,
	OrgDashboardResponse,
} from "../../../shared/types/api";

// --- Dashboard ---
export function useDashboard(orgId: string | undefined) {
	return useQuery({
		queryKey: ["dashboard", orgId],
		queryFn: () => adminApi.get<OrgDashboardResponse>(`/orgs/${orgId}/dashboard`),
		enabled: Boolean(orgId),
	});
}

// --- Forms ---
export function useForms(orgId: string | undefined) {
	return useQuery({
		queryKey: ["forms", orgId],
		queryFn: () => fetchForms(orgId!),
		enabled: Boolean(orgId),
	});
}

export function useForm(formId: string | undefined) {
	return useQuery({
		queryKey: ["form", formId],
		queryFn: () => fetchForm(formId!),
		enabled: Boolean(formId),
	});
}

export function useGenerateForm(orgId: string) {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (prompt: string) => generateForm(orgId, prompt),
		onSuccess: () => queryClient.invalidateQueries({ queryKey: ["forms"] }),
	});
}

export function useCreateForm(orgId: string) {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (payload: FormCreatePayload) => createForm(orgId, payload),
		onSuccess: () => queryClient.invalidateQueries({ queryKey: ["forms"] }),
	});
}

export function useUpdateForm() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ formId, payload }: { formId: string; payload: Parameters<typeof updateForm>[1] }) =>
			updateForm(formId, payload),
		onSuccess: (_data, vars) => {
			queryClient.invalidateQueries({ queryKey: ["form", vars.formId] });
			queryClient.invalidateQueries({ queryKey: ["forms"] });
		},
	});
}

export function usePublishForm() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: publishForm,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["forms"] });
			queryClient.invalidateQueries({ queryKey: ["dashboard"] });
		},
	});
}

export function useUnpublishForm() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: unpublishForm,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["forms"] });
			queryClient.invalidateQueries({ queryKey: ["dashboard"] });
		},
	});
}

export function useDuplicateForm() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: duplicateForm,
		onSuccess: () => queryClient.invalidateQueries({ queryKey: ["forms"] }),
	});
}

// --- Submissions ---
export function useSubmissions(formId: string | undefined) {
	return useQuery({
		queryKey: ["submissions", formId],
		queryFn: () => fetchSubmissions(formId!),
		enabled: Boolean(formId),
	});
}

export function useExportCsv() {
	return useMutation({ mutationFn: exportCsv });
}

// --- Templates ---
export function useTemplates() {
	return useQuery({
		queryKey: ["templates"],
		queryFn: fetchTemplates,
		staleTime: 60_000 * 5,
	});
}

// --- Analytics ---
export function useFormAnalytics(formId: string | undefined) {
	return useQuery({
		queryKey: ["analytics", formId],
		queryFn: () => fetchFormAnalytics(formId!),
		enabled: Boolean(formId),
	});
}

// --- Billing ---
export function useBilling(orgId: string | undefined) {
	return useQuery({
		queryKey: ["billing", orgId],
		queryFn: () => fetchBilling(orgId!),
		enabled: Boolean(orgId),
	});
}

// --- Team ---
export function useMembers(orgId: string | undefined) {
	return useQuery({
		queryKey: ["members", orgId],
		queryFn: () => fetchMembers(orgId!),
		enabled: Boolean(orgId),
	});
}
