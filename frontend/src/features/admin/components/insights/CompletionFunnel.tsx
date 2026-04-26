import type { DropoffStep } from "../../../../shared/types/api";

export function CompletionFunnel({ steps, totalSessions }: { steps: DropoffStep[]; totalSessions: number }) {
	if (!steps.length) {
		return <p className="text-[13px] text-text-tertiary">No field data available.</p>;
	}

	return (
		<div className="space-y-3">
			{steps.map((step) => {
				const pct = totalSessions > 0 ? Math.round((step.sessions_answered / totalSessions) * 100) : 0;
				const isHighDropoff = step.dropoff_pct > 20;
				return (
					<div key={step.field_key}>
						<div className="flex justify-between items-center text-[12px] mb-1">
							<span className="text-text-secondary truncate max-w-[60%]" title={step.field_name}>
								{step.field_name}
							</span>
							<span className={`font-medium tabular-nums ${isHighDropoff ? "text-clay-500" : "text-text-primary"}`}>
								{step.sessions_answered} / {totalSessions}
								{isHighDropoff && (
									<span className="ml-1 text-clay-400 text-[11px]">↓{step.dropoff_pct.toFixed(0)}%</span>
								)}
							</span>
						</div>
						<div className="h-2 rounded-full bg-stone-100 overflow-hidden">
							<div
								className={`h-full rounded-full transition-all duration-500 ${isHighDropoff ? "bg-clay-400/80" : "bg-forest-400/90"}`}
								style={{ width: `${pct}%` }}
							/>
						</div>
					</div>
				);
			})}
		</div>
	);
}
