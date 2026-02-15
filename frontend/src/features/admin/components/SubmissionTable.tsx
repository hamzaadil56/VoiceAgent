/** Submissions table component */
import type { SubmissionRow } from "../../../shared/types/api";

interface SubmissionTableProps {
	submissions: SubmissionRow[];
}

export function SubmissionTable({ submissions }: SubmissionTableProps) {
	// Get all unique field keys across submissions
	const fieldKeys = Array.from(
		new Set(submissions.flatMap((s) => Object.keys(s.answers))),
	);

	if (submissions.length === 0) {
		return (
			<div className="glass-elevated rounded-2xl p-12 border border-border/40 text-center">
				<h2 className="text-xl font-heading text-text-primary mb-2">No submissions yet</h2>
				<p className="text-text-secondary">
					Share your form link to start collecting responses.
				</p>
			</div>
		);
	}

	return (
		<div className="glass rounded-2xl border border-border/40 overflow-hidden">
			<div className="overflow-x-auto">
				<table className="w-full text-sm">
					<thead>
						<tr className="border-b border-border/40">
							<th className="px-4 py-3 text-left text-text-tertiary font-medium">#</th>
							<th className="px-4 py-3 text-left text-text-tertiary font-medium">Completed</th>
							{fieldKeys.map((key) => (
								<th key={key} className="px-4 py-3 text-left text-text-tertiary font-medium whitespace-nowrap">
									{key}
								</th>
							))}
						</tr>
					</thead>
					<tbody>
						{submissions.map((sub, i) => (
							<tr
								key={sub.submission_id}
								className="border-b border-border/20 hover:bg-surface/50"
							>
								<td className="px-4 py-3 text-text-tertiary">{i + 1}</td>
								<td className="px-4 py-3 text-text-secondary whitespace-nowrap">
									{new Date(sub.completed_at).toLocaleDateString(undefined, {
										year: "numeric",
										month: "short",
										day: "numeric",
										hour: "2-digit",
										minute: "2-digit",
									})}
								</td>
								{fieldKeys.map((key) => (
									<td key={key} className="px-4 py-3 text-text-primary max-w-[200px] truncate">
										{sub.answers[key] || "-"}
									</td>
								))}
							</tr>
						))}
					</tbody>
				</table>
			</div>
			<div className="px-4 py-3 border-t border-border/40 text-sm text-text-tertiary">
				{submissions.length} submission{submissions.length !== 1 ? "s" : ""}
			</div>
		</div>
	);
}
