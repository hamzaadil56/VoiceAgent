export function OverallSummaryCard({ summary, generatedAt }: { summary: string; generatedAt: string }) {
	const date = new Date(generatedAt).toLocaleString();
	return (
		<div className="rounded-xl border border-forest-200 bg-forest-50 p-5">
			<div className="flex items-center justify-between mb-3">
				<div className="flex items-center gap-2">
					<div className="w-2 h-2 rounded-full bg-forest-400" />
					<p className="text-[12px] font-semibold text-forest-700 uppercase tracking-wider">
						AI Overall Summary
					</p>
				</div>
				<p className="text-[11px] text-text-tertiary">Generated {date}</p>
			</div>
			<p className="text-[14px] text-text-secondary leading-relaxed">{summary}</p>
		</div>
	);
}
