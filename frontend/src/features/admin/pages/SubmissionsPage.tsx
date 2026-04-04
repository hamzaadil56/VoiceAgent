import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../../app/AuthProvider";
import { exportCsv, fetchSubmissions } from "../api/adminApi";
import { SubmissionTable } from "../components/SubmissionTable";
import { AdminShell, EmptyState, PageBody, PageHeader } from "../../../shared/ui/Layout";
import type { SubmissionRow } from "../../../shared/types/api";

export default function SubmissionsPage() {
	const { formId } = useParams<{ formId: string }>();
	const { admin, logout } = useAuth();
	const navigate = useNavigate();
	const [submissions, setSubmissions] = useState<SubmissionRow[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [exporting, setExporting] = useState(false);
	const [exportStatus, setExportStatus] = useState<string | null>(null);

	useEffect(() => {
		if (!formId) return;
		setLoading(true);
		fetchSubmissions(formId)
			.then((res) => setSubmissions(res.rows))
			.catch((err) => setError(err.message))
			.finally(() => setLoading(false));
	}, [formId]);

	const handleExport = async () => {
		if (!formId) return;
		setExporting(true);
		setExportStatus(null);
		try {
			const res = await exportCsv(formId);
			setExportStatus(`Export created: ${res.row_count} rows`);
		} catch (err) {
			setExportStatus(err instanceof Error ? err.message : "Export failed");
		} finally {
			setExporting(false);
		}
	};

	return (
		<AdminShell email={admin?.email} onLogout={() => { logout(); navigate("/admin/login"); }}>
			<PageHeader
				title="Submissions"
				subtitle={formId ? `Form: ${formId}` : undefined}
				backTo="/admin"
				backLabel="Dashboard"
				actions={
					<button
						onClick={handleExport}
						disabled={exporting || submissions.length === 0}
						className="px-5 py-[9px] rounded-md font-medium text-[13px] text-white bg-forest-500 hover:bg-forest-600 transition-all duration-150 disabled:opacity-50 shadow-forest inline-flex items-center gap-1.5"
					>
						<svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
							<path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
						</svg>
						{exporting ? "Exporting..." : "Export CSV"}
					</button>
				}
			/>
			<PageBody>
				{exportStatus && (
					<div className="rounded-md p-3 border-[0.5px] border-stone-100 bg-stone-50 text-[13px] text-text-secondary mb-4">
						{exportStatus}
					</div>
				)}

				{loading ? (
					<div className="flex justify-center py-20">
						<div className="w-6 h-6 border-2 border-forest-500 border-t-transparent rounded-full animate-spin" />
					</div>
				) : error ? (
					<div className="rounded-lg p-8 border text-center" style={{ background: "var(--error-bg)", borderColor: "var(--error-border)" }}>
						<p className="text-sm text-error">{error}</p>
					</div>
				) : submissions.length === 0 ? (
					<EmptyState
						title="No submissions yet"
						description="Submissions will appear here once consumers complete your form."
					/>
				) : (
					<SubmissionTable submissions={submissions} />
				)}
			</PageBody>
		</AdminShell>
	);
}
