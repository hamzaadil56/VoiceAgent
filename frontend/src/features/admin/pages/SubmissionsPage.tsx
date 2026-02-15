/** Submissions page for a specific form */
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { exportCsv, fetchSubmissions } from "../api/adminApi";
import { SubmissionTable } from "../components/SubmissionTable";
import type { SubmissionRow } from "../../../shared/types/api";

export default function SubmissionsPage() {
	const { formId } = useParams<{ formId: string }>();
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
		<div className="max-w-6xl mx-auto py-8 px-4 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<Link to="/admin" className="text-sm text-text-tertiary hover:text-accent-primary mb-2 inline-block">
						&larr; Back to Dashboard
					</Link>
					<h1 className="text-2xl font-heading font-bold text-text-primary">
						Submissions
					</h1>
					<p className="text-sm text-text-tertiary mt-1">Form: {formId}</p>
				</div>
				<button
					onClick={handleExport}
					disabled={exporting || submissions.length === 0}
					className="px-4 py-2.5 rounded-xl bg-accent-primary text-bg-primary font-semibold hover:opacity-90 disabled:opacity-50"
				>
					{exporting ? "Exporting..." : "Export CSV"}
				</button>
			</div>

			{exportStatus && (
				<div className="glass rounded-xl p-3 border border-border/40 text-sm text-text-secondary">
					{exportStatus}
				</div>
			)}

			{loading ? (
				<div className="flex justify-center py-20">
					<div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
				</div>
			) : error ? (
				<div className="glass-elevated rounded-2xl p-8 border border-error/30 text-center">
					<p className="text-error">{error}</p>
				</div>
			) : (
				<SubmissionTable submissions={submissions} />
			)}
		</div>
	);
}
