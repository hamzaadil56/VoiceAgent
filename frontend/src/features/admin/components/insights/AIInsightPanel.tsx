import type { FieldAIInsight } from "../../../../shared/types/api";

const sentimentConfig: Record<string, { label: string; className: string }> = {
	positive: { label: "Positive", className: "bg-sage-100 text-sage-700" },
	negative: { label: "Negative", className: "bg-clay-100 text-clay-700" },
	mixed: { label: "Mixed", className: "bg-amber-50 text-amber-700" },
	neutral: { label: "Neutral", className: "bg-stone-100 text-stone-600" },
};

export function AIInsightPanel({ insight }: { insight: FieldAIInsight }) {
	const sentiment = sentimentConfig[insight.sentiment] ?? sentimentConfig.neutral;

	return (
		<div className="rounded-lg border border-forest-100 bg-forest-50/40 p-4 space-y-3 h-full">
			<div className="flex items-center justify-between">
				<p className="text-[11px] font-semibold text-forest-700 uppercase tracking-wider">AI Insight</p>
				<span className={`text-[11px] font-medium px-2 py-0.5 rounded-full ${sentiment.className}`}>
					{sentiment.label}
				</span>
			</div>

			<p className="text-[13px] text-text-secondary leading-relaxed">{insight.summary}</p>

			{insight.themes.length > 0 && (
				<div>
					<p className="text-[11px] text-text-tertiary uppercase tracking-wider mb-1.5">Themes</p>
					<div className="flex flex-wrap gap-1.5">
						{insight.themes.map((theme, i) => (
							<span
								key={i}
								className="text-[11px] px-2 py-0.5 rounded-full bg-forest-100 text-forest-700 font-medium"
							>
								{theme}
							</span>
						))}
					</div>
				</div>
			)}

			{insight.notable_responses.length > 0 && (
				<div>
					<p className="text-[11px] text-text-tertiary uppercase tracking-wider mb-1.5">Notable Responses</p>
					<div className="space-y-2">
						{insight.notable_responses.map((quote, i) => (
							<blockquote
								key={i}
								className="pl-3 border-l-2 border-forest-300 text-[12px] text-text-secondary italic leading-relaxed"
							>
								"{quote}"
							</blockquote>
						))}
					</div>
				</div>
			)}
		</div>
	);
}
