import type { FieldValueCount } from "../../../../shared/types/api";

export function TopValuesList({ values, total }: { values: FieldValueCount[]; total: number }) {
	if (!values.length) {
		return <p className="text-[13px] text-text-tertiary">No responses yet.</p>;
	}

	const maxCount = Math.max(1, ...values.map((v) => v.count));

	return (
		<div className="space-y-2">
			{values.map((v, i) => (
				<div key={`${v.value}-${i}`}>
					<div className="flex justify-between items-baseline text-[12px] mb-0.5">
						<span className="text-text-secondary truncate max-w-[70%]" title={v.value}>
							{v.value}
						</span>
						<span className="text-text-primary font-medium tabular-nums">
							{v.count} <span className="text-text-tertiary font-normal">({v.pct.toFixed(0)}%)</span>
						</span>
					</div>
					<div className="h-1.5 rounded-full bg-stone-100 overflow-hidden">
						<div
							className="h-full rounded-full bg-forest-400/80"
							style={{ width: `${Math.round((v.count / maxCount) * 100)}%` }}
						/>
					</div>
				</div>
			))}
			{total > values.length && (
				<p className="text-[11px] text-text-tertiary pt-1">
					Showing top {values.length} of {total} unique responses
				</p>
			)}
		</div>
	);
}
