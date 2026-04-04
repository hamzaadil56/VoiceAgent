import type { SubmissionRow } from "../../../shared/types/api";

interface SubmissionTableProps {
	submissions: SubmissionRow[];
}

export function SubmissionTable({ submissions }: SubmissionTableProps) {
	const fieldKeys = Array.from(
		new Set(submissions.flatMap((s) => Object.keys(s.answers))),
	);

	if (submissions.length === 0) return null;

	return (
		<div className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 overflow-hidden">
			<div className="overflow-x-auto">
				<table className="w-full border-collapse text-[13px]">
					<thead>
						<tr className="border-b border-stone-100">
							<th className="px-3 py-2.5 text-left text-[11px] font-medium uppercase tracking-[0.05em] text-text-tertiary">
								#
							</th>
							<th className="px-3 py-2.5 text-left text-[11px] font-medium uppercase tracking-[0.05em] text-text-tertiary">
								Completed
							</th>
							{fieldKeys.map((key) => (
								<th
									key={key}
									className="px-3 py-2.5 text-left text-[11px] font-medium uppercase tracking-[0.05em] text-text-tertiary whitespace-nowrap"
								>
									{key}
								</th>
							))}
						</tr>
					</thead>
					<tbody>
						{submissions.map((sub, i) => (
							<tr
								key={sub.submission_id}
								className="border-b border-stone-100 transition-colors hover:bg-stone-50"
							>
								<td className="px-3 py-2.5 text-text-tertiary">
									{i + 1}
								</td>
								<td className="px-3 py-2.5 text-text-secondary whitespace-nowrap">
									{new Date(sub.completed_at).toLocaleDateString(undefined, {
										year: "numeric",
										month: "short",
										day: "numeric",
										hour: "2-digit",
										minute: "2-digit",
									})}
								</td>
								{fieldKeys.map((key) => (
									<td key={key} className="px-3 py-2.5 text-text-primary max-w-[200px] truncate">
										{sub.answers[key] || (
											<span className="text-text-tertiary">-</span>
										)}
									</td>
								))}
							</tr>
						))}
					</tbody>
				</table>
			</div>
			<div className="px-3 py-2.5 border-t border-stone-100 text-[11px] font-medium uppercase tracking-[0.05em] text-text-tertiary">
				{submissions.length} submission{submissions.length !== 1 ? "s" : ""}
			</div>
		</div>
	);
}
