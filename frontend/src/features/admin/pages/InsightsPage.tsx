import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../../app/AuthProvider";
import { useExportCsv, useFieldDistributions, useFormAnalytics, useGenerateAIInsights } from "../hooks/useAdminQueries";
import { AdminShell, EmptyState, PageBody, PageHeader } from "../../../shared/ui/Layout";
import { KpiCards } from "../components/insights/KpiCards";
import { CompletionFunnel } from "../components/insights/CompletionFunnel";
import { FieldDistributionCard } from "../components/insights/FieldDistributionCard";
import { OverallSummaryCard } from "../components/insights/OverallSummaryCard";
import type { FormAIInsightsResponse } from "../../../shared/types/api";

const CHANNEL_LABELS: Record<string, string> = { chat: "Chat", voice: "Voice", chat_voice: "Chat + Voice" };

function ChannelBreakdown({ channels }: { channels: Record<string, number> }) {
	const sum = Object.values(channels).reduce((a, n) => a + n, 0);
	const total = sum > 0 ? sum : 1;
	if (sum === 0) {
		return <p className="text-[13px] text-text-tertiary">No completed responses yet.</p>;
	}
	return (
		<div className="space-y-3">
			{(["chat", "voice", "chat_voice"] as const).map((key) => {
				const n = channels[key] ?? 0;
				const pct = Math.round((100 * n) / total);
				return (
					<div key={key}>
						<div className="flex justify-between text-[12px] mb-1">
							<span className="text-text-secondary">{CHANNEL_LABELS[key]}</span>
							<span className="text-text-primary font-medium tabular-nums">{n}</span>
						</div>
						<div className="h-2 rounded-full bg-stone-100 overflow-hidden">
							<div
								className="h-full rounded-full bg-forest-400/90 transition-all duration-500"
								style={{ width: `${pct}%` }}
							/>
						</div>
					</div>
				);
			})}
		</div>
	);
}

export default function InsightsPage() {
	const { formId } = useParams<{ formId: string }>();
	const { admin, logout } = useAuth();
	const navigate = useNavigate();

	const { data: analytics, isLoading: analyticsLoading } = useFormAnalytics(formId);
	const { data: distributions, isLoading: distLoading } = useFieldDistributions(formId);
	const generateMutation = useGenerateAIInsights();
	const exportMutation = useExportCsv();

	const [aiInsights, setAiInsights] = useState<FormAIInsightsResponse | null>(null);
	const [aiError, setAiError] = useState<string | null>(null);

	const isLoading = analyticsLoading || distLoading;

	const handleGenerateInsights = async () => {
		if (!formId) return;
		setAiError(null);
		try {
			const result = await generateMutation.mutateAsync(formId);
			setAiInsights(result);
		} catch (err) {
			setAiError(err instanceof Error ? err.message : "Failed to generate insights.");
		}
	};

	const handleExport = async () => {
		if (!formId) return;
		try {
			await exportMutation.mutateAsync(formId);
		} catch { /* silently handled below */ }
	};

	const aiInsightMap = new Map(
		aiInsights?.field_insights.map((fi) => [fi.field_key, fi]) ?? []
	);

	return (
		<AdminShell email={admin?.email} onLogout={() => { logout(); navigate("/admin/login"); }}>
			<PageHeader
				title="Insights"
				subtitle={formId ? `Form: ${formId}` : undefined}
				backTo={`/admin/forms/${formId}/submissions`}
				backLabel="Submissions"
				actions={
					<div className="flex items-center gap-2">
						<button
							onClick={handleGenerateInsights}
							disabled={generateMutation.isPending || !distributions?.fields.length}
							className="px-4 py-[9px] rounded-md font-medium text-[13px] text-white bg-forest-500 hover:bg-forest-600 transition-all duration-150 disabled:opacity-50 shadow-forest inline-flex items-center gap-1.5"
						>
							{generateMutation.isPending ? (
								<>
									<div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
									Analyzing…
								</>
							) : aiInsights ? "Regenerate AI Insights" : "Generate AI Insights"}
						</button>
						<button
							onClick={handleExport}
							disabled={exportMutation.isPending || !analytics?.total_submissions}
							className="px-4 py-[9px] rounded-md font-medium text-[13px] text-text-secondary bg-white border border-stone-200 hover:bg-stone-50 transition-all duration-150 disabled:opacity-50 inline-flex items-center gap-1.5"
						>
							<svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
								<path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
							</svg>
							{exportMutation.isPending ? "Exporting…" : "Export CSV"}
						</button>
					</div>
				}
			/>

			<PageBody>
				{isLoading ? (
					<div className="flex justify-center py-20">
						<div className="w-6 h-6 border-2 border-forest-500 border-t-transparent rounded-full animate-spin" />
					</div>
				) : !analytics || !distributions ? (
					<EmptyState
						title="No data yet"
						description="Submit responses to this form to see insights here."
					/>
				) : analytics.total_submissions === 0 ? (
					<EmptyState
						title="No submissions yet"
						description="Insights will appear here once consumers complete your form."
					/>
				) : (
					<div className="space-y-6">
						{/* KPI row */}
						<KpiCards analytics={analytics} />

						{/* Funnel + Channel row */}
						<div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
							<div className="lg:col-span-2 rounded-xl border border-stone-200 bg-white shadow-sm p-5">
								<p className="text-[12px] font-semibold text-text-tertiary uppercase tracking-wider mb-4">
									Completion Funnel
								</p>
								<CompletionFunnel
									steps={analytics.dropoff_funnel}
									totalSessions={analytics.total_sessions}
								/>
							</div>
							<div className="rounded-xl border border-stone-200 bg-white shadow-sm p-5">
								<p className="text-[12px] font-semibold text-text-tertiary uppercase tracking-wider mb-4">
									By Channel
								</p>
								<ChannelBreakdown channels={analytics.channel_breakdown} />
							</div>
						</div>

						{/* AI error */}
						{aiError && (
							<div className="rounded-md p-3 border border-clay-200 bg-clay-50 text-[13px] text-clay-700">
								{aiError}
							</div>
						)}

						{/* AI overall summary */}
						{aiInsights && (
							<OverallSummaryCard
								summary={aiInsights.overall_summary}
								generatedAt={aiInsights.generated_at}
							/>
						)}

						{/* Per-field distribution cards */}
						{distributions.fields.length > 0 ? (
							<div className="space-y-4">
								<p className="text-[12px] font-semibold text-text-tertiary uppercase tracking-wider">
									Response Distributions
								</p>
								{distributions.fields.map((dist) => (
									<FieldDistributionCard
										key={dist.field_key}
										dist={dist}
										aiInsight={aiInsightMap.get(dist.field_key)}
									/>
								))}
							</div>
						) : (
							<EmptyState
								title="No field data"
								description="This form has no fields with responses yet."
							/>
						)}

						{/* Hint to generate AI insights if not done yet */}
						{!aiInsights && !generateMutation.isPending && distributions.fields.some(
							(f) => f.field_type === "text" || f.field_type === "url"
						) && (
							<div className="rounded-xl border border-dashed border-forest-200 bg-forest-50/50 p-6 text-center">
								<p className="text-[14px] font-medium text-forest-700 mb-1">
									AI Insights available
								</p>
								<p className="text-[13px] text-text-tertiary mb-3">
									This form has text responses. Click "Generate AI Insights" to get themes, sentiment, and key quotes.
								</p>
								<button
									onClick={handleGenerateInsights}
									className="px-4 py-2 rounded-md text-[13px] font-medium text-white bg-forest-500 hover:bg-forest-600 transition-all"
								>
									Generate AI Insights
								</button>
							</div>
						)}

						<div className="pt-2 text-center">
							<Link
								to={`/admin/forms/${formId}/submissions`}
								className="text-[13px] text-text-tertiary hover:text-text-secondary underline-offset-2 hover:underline"
							>
								View raw submissions table
							</Link>
						</div>
					</div>
				)}
			</PageBody>
		</AdminShell>
	);
}
