import type { FormAnalytics } from "../../../../shared/types/api";

function formatDuration(seconds: number): string {
	const m = Math.floor(seconds / 60);
	const s = Math.floor(seconds % 60);
	return `${m}:${s.toString().padStart(2, "0")}`;
}

function formatInt(n: number): string {
	return new Intl.NumberFormat().format(n);
}

function KpiCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
	return (
		<div className="rounded-xl border border-stone-200 bg-white p-5 shadow-sm">
			<p className="text-[12px] font-medium text-text-tertiary uppercase tracking-wider mb-1">{label}</p>
			<p className="text-[28px] font-semibold text-text-primary leading-none">{value}</p>
			{sub && <p className="text-[12px] text-text-tertiary mt-1">{sub}</p>}
		</div>
	);
}

export function KpiCards({ analytics }: { analytics: FormAnalytics }) {
	const topChannel = Object.entries(analytics.channel_breakdown).sort((a, b) => b[1] - a[1])[0];
	const channelLabel: Record<string, string> = { chat: "Chat", voice: "Voice", chat_voice: "Chat + Voice" };

	return (
		<div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
			<KpiCard
				label="Total Submissions"
				value={formatInt(analytics.total_submissions)}
				sub={`${formatInt(analytics.total_sessions)} sessions`}
			/>
			<KpiCard
				label="Completion Rate"
				value={`${analytics.completion_rate_pct.toFixed(1)}%`}
				sub="of all sessions"
			/>
			<KpiCard
				label="Avg Duration"
				value={analytics.avg_completion_seconds ? formatDuration(analytics.avg_completion_seconds) : "—"}
				sub="minutes:seconds"
			/>
			<KpiCard
				label="Top Channel"
				value={topChannel ? (channelLabel[topChannel[0]] ?? topChannel[0]) : "—"}
				sub={topChannel ? `${formatInt(topChannel[1])} submissions` : undefined}
			/>
		</div>
	);
}
