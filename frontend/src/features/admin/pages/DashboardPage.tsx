import { useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../../app/AuthProvider";
import { useDashboard } from "../hooks/useAdminQueries";
import { AdminShell, EmptyState, PageBody, PageHeader } from "../../../shared/ui/Layout";

function formatInt(n: number): string {
	return new Intl.NumberFormat().format(n);
}

function formatDuration(seconds: number): string {
	const m = Math.floor(seconds / 60);
	const s = Math.floor(seconds % 60);
	return `${m}:${s.toString().padStart(2, "0")}`;
}

function formatRelativeShort(iso: string): string {
	const diffSec = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 1000));
	if (diffSec < 60) return `${diffSec}s ago`;
	const diffMin = Math.floor(diffSec / 60);
	if (diffMin < 60) return `${diffMin}m ago`;
	const diffH = Math.floor(diffMin / 60);
	if (diffH < 48) return `${diffH}h ago`;
	const diffD = Math.floor(diffH / 24);
	return `${diffD}d ago`;
}

function formatTodayLabel(): string {
	return new Intl.DateTimeFormat("en-US", {
		month: "short",
		day: "numeric",
		year: "numeric",
	}).format(new Date());
}

function TrendLine({ value, suffix }: { value: number | null | undefined; suffix: string }) {
	if (value == null) {
		return <span className="text-[12px] text-text-tertiary">No prior period to compare</span>;
	}
	const positive = value >= 0;
	return (
		<span
			className={`text-[12px] font-medium ${positive ? "text-sage-600" : "text-clay-500"}`}
		>
			{positive ? "↗" : "↘"} {Math.abs(value).toFixed(1)}%{suffix}
		</span>
	);
}

function AreaChart({ data }: { data: { date: string; count: number }[] }) {
	const w = 720;
	const h = 160;
	const pad = { t: 12, r: 8, b: 28, l: 8 };
	const innerW = w - pad.l - pad.r;
	const innerH = h - pad.t - pad.b;
	const max = Math.max(1, ...data.map((d) => d.count));
	const pts = data.map((d, i) => {
		const x = pad.l + (innerW * i) / Math.max(1, data.length - 1);
		const y = pad.t + innerH - (innerH * d.count) / max;
		return { x, y, ...d };
	});
	const lineD = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(" ");
	const areaD = `${lineD} L ${pts[pts.length - 1]?.x ?? pad.l} ${pad.t + innerH} L ${pts[0]?.x ?? pad.l} ${pad.t + innerH} Z`;
	const mid = Math.ceil(max / 2);
	return (
		<svg viewBox={`0 0 ${w} ${h}`} className="w-full h-[180px]" preserveAspectRatio="none">
			<defs>
				<linearGradient id="dashArea" x1="0" y1="0" x2="0" y2="1">
					<stop offset="0%" stopColor="rgb(45, 106, 90)" stopOpacity="0.2" />
					<stop offset="100%" stopColor="rgb(45, 106, 90)" stopOpacity="0" />
				</linearGradient>
			</defs>
			<text x={pad.l} y={16} className="fill-stone-400 text-[11px]" fontFamily="system-ui">
				{mid}
			</text>
			<text x={pad.l} y={pad.t + innerH / 2 + 4} className="fill-stone-400 text-[11px]" fontFamily="system-ui">
				{Math.floor(mid / 2)}
			</text>
			<path d={areaD} fill="url(#dashArea)" />
			<path
				d={lineD}
				fill="none"
				stroke="rgb(45, 106, 90)"
				strokeWidth={2}
				strokeLinecap="round"
				strokeLinejoin="round"
			/>
			{pts.map((p, i) => (
				<circle key={`${p.date}-${i}`} cx={p.x} cy={p.y} r={data.length > 20 ? 0 : 3.5} className="fill-forest-500" />
			))}
			<text
				x={pad.l}
				y={h - 6}
				className="fill-stone-500 text-[10px] font-medium uppercase tracking-wider"
				fontFamily="system-ui"
			>
				{data[0]?.date.slice(5)} → {data[data.length - 1]?.date.slice(5)}
			</text>
		</svg>
	);
}

function ChannelBars({ channels }: { channels: Record<string, number> }) {
	const labels: Record<string, string> = { chat: "Chat", voice: "Voice", chat_voice: "Chat + voice" };
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
							<span className="text-text-secondary">{labels[key] ?? key}</span>
							<span className="text-text-primary font-medium tabular-nums">{formatInt(n)}</span>
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

export default function DashboardPage() {
	const { admin, logout } = useAuth();
	const navigate = useNavigate();

	const orgId = admin?.memberships[0]?.org_id;
	const { data: dash, isLoading: loading, error: queryError } = useDashboard(orgId);
	const error = queryError ? (queryError as Error).message : null;

	const handleLogout = () => {
		logout();
		navigate("/admin/login");
	};

	const topForms = useMemo(() => (dash?.forms ?? []).slice(0, 8), [dash?.forms]);

	return (
		<AdminShell email={admin?.email} onLogout={handleLogout}>
			<PageHeader
				title="The Workspace"
				subtitle="Overview of agent responses, completion, and activity across your forms."
				actions={
					<div className="flex items-center gap-3">
						<div
							className="hidden sm:flex items-center gap-2 px-3 py-2 rounded-md border border-stone-200 bg-bg-base text-[12px] text-text-secondary"
							title="Today"
						>
							<svg className="w-3.5 h-3.5 text-text-tertiary" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
								<rect x="4" y="5" width="16" height="15" rx="1.5" />
								<path strokeLinecap="round" d="M8 3v4m8-4v4M4 11h16" />
							</svg>
							<span className="tabular-nums">{formatTodayLabel()}</span>
						</div>
						<Link
							to="/admin/forms/new"
							className="px-5 py-[9px] rounded-md font-medium text-[13px] text-white bg-forest-500 hover:bg-forest-600 transition-all duration-150 shadow-forest inline-flex items-center gap-1.5"
						>
							<svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
								<line x1="12" y1="5" x2="12" y2="19" />
								<line x1="5" y1="12" x2="19" y2="12" />
							</svg>
							New Form
						</Link>
					</div>
				}
			/>
			<PageBody>
				<div className="max-w-[1280px] w-full mx-auto space-y-8 pb-10">
					{loading ? (
						<div className="flex justify-center py-24">
							<div className="w-6 h-6 border-2 border-forest-500 border-t-transparent rounded-full animate-spin" />
						</div>
					) : error ? (
						<div
							className="rounded-lg p-8 border text-center"
							style={{ background: "var(--error-bg)", borderColor: "var(--error-border)" }}
						>
							<p className="text-sm text-error">{error}</p>
						</div>
					) : !dash ? null : dash.forms.length === 0 && dash.total_submissions === 0 ? (
						<EmptyState
							title="No forms yet"
							description="Create your first conversational form to start collecting responses."
							action={
								<Link
									to="/admin/forms/new"
									className="px-5 py-[9px] rounded-md font-medium text-[13px] text-white bg-forest-500 hover:bg-forest-600 transition-all duration-150 shadow-forest inline-flex items-center gap-1.5"
								>
									<svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
										<line x1="12" y1="5" x2="12" y2="19" />
										<line x1="5" y1="12" x2="19" y2="12" />
									</svg>
									Create First Form
								</Link>
							}
						/>
					) : (
						<>
							<section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
								<div className="rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-5 shadow-sm">
									<p className="text-[11px] uppercase tracking-[0.08em] text-text-tertiary font-medium mb-2">
										Total responses
									</p>
									<p className="font-heading text-[28px] text-text-primary tabular-nums leading-none">
										{formatInt(dash.total_submissions)}
									</p>
									<p className="mt-2">
										<TrendLine value={dash.submissions_trend_pct} suffix=" vs prior week" />
									</p>
								</div>
								<div className="rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-5 shadow-sm">
									<p className="text-[11px] uppercase tracking-[0.08em] text-text-tertiary font-medium mb-2">
										Completion rate
									</p>
									<p className="font-heading text-[28px] text-text-primary tabular-nums leading-none">
										{dash.completion_rate_pct.toFixed(0)}%
									</p>
									<p className="mt-2">
										<TrendLine value={dash.completion_rate_trend_pct} suffix=" pts vs prior week" />
									</p>
								</div>
								<div className="rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-5 shadow-sm">
									<p className="text-[11px] uppercase tracking-[0.08em] text-text-tertiary font-medium mb-2">
										Active agents
									</p>
									<p className="font-heading text-[28px] text-text-primary tabular-nums leading-none">
										{dash.published_forms}
									</p>
									<p className="text-[12px] text-text-tertiary mt-2">
										{dash.draft_forms} draft{dash.draft_forms !== 1 ? "s" : ""} · {dash.forms.length} total
									</p>
								</div>
								<div className="rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-5 shadow-sm">
									<p className="text-[11px] uppercase tracking-[0.08em] text-text-tertiary font-medium mb-2">
										Avg. session length
									</p>
									<p className="font-heading text-[28px] text-text-primary tabular-nums leading-none">
										{dash.avg_completion_seconds != null
											? formatDuration(dash.avg_completion_seconds)
											: "—"}
									</p>
									<p className="text-[12px] text-text-tertiary mt-2">From start to completed response</p>
								</div>
							</section>

							<section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
								<div className="lg:col-span-2 rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-6 shadow-sm">
									<div className="flex items-start justify-between gap-4 mb-2">
										<div>
											<h2 className="font-heading text-[20px] text-text-primary">Responses over time</h2>
											<p className="text-[13px] text-text-secondary mt-0.5">Last 14 days · completed submissions</p>
										</div>
										<span className="text-[12px] tabular-nums text-forest-600 font-medium bg-forest-50 px-2.5 py-1 rounded-md">
											{formatInt(dash.submissions_last_7d)} last 7d
										</span>
									</div>
									<AreaChart data={dash.daily_submissions} />
								</div>
								<div className="rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-6 shadow-sm">
									<h2 className="font-heading text-[20px] text-text-primary mb-1">By channel</h2>
									<p className="text-[13px] text-text-secondary mb-5">Completed responses</p>
									<ChannelBars channels={dash.submissions_by_channel} />
								</div>
							</section>

							<section className="grid grid-cols-1 lg:grid-cols-5 gap-6">
								<div className="lg:col-span-3 space-y-4">
									<div className="flex items-center justify-between">
										<h2 className="font-heading text-[20px] text-text-primary">Your forms</h2>
										<Link
											to="/admin/forms/new"
											className="text-[12px] font-medium uppercase tracking-wider text-forest-600 hover:text-forest-700"
										>
											New form
										</Link>
									</div>
									<div className="space-y-3">
										{topForms.map((form) => (
											<div
												key={form.form_id}
												className={`rounded-xl border p-5 flex flex-col sm:flex-row sm:items-center gap-4 transition-all duration-150 hover:border-forest-200/80 hover:shadow-sm ${
													form.status === "draft"
														? "border-dashed border-stone-300/90 bg-stone-50/50 opacity-95"
														: "border-[0.5px] border-stone-200 bg-bg-base"
												}`}
											>
												<div className="flex-1 min-w-0">
													<div className="flex flex-wrap items-center gap-2 mb-1">
														<h3 className="font-heading font-medium text-[16px] text-text-primary truncate">
															{form.title}
														</h3>
														<StatusBadge status={form.status} />
														<span className="text-[11px] uppercase tracking-wide text-text-tertiary">
															{form.mode.replace("_", " + ")}
														</span>
													</div>
													<p className="font-mono text-[12px] text-text-tertiary">
														{formatInt(form.submission_count)} response{form.submission_count !== 1 ? "s" : ""}
													</p>
												</div>
												<div className="flex flex-wrap gap-2">
													<Link
														to={`/admin/forms/${form.form_id}`}
														className="px-3 py-[7px] rounded-md text-[13px] text-text-secondary bg-bg-base border-[0.5px] border-stone-200 hover:border-stone-300"
													>
														Edit
													</Link>
													<Link
														to={`/admin/forms/${form.form_id}/submissions`}
														className="px-3 py-[7px] rounded-md text-[13px] text-text-secondary bg-bg-base border-[0.5px] border-stone-200 hover:border-stone-300"
													>
														Submissions
													</Link>
													{form.status === "published" && (
														<Link
															to={`/f/${form.slug}`}
															target="_blank"
															className="px-3 py-[7px] rounded-md text-[13px] text-forest-600 bg-forest-50 border-[0.5px] border-forest-200 hover:bg-forest-100"
														>
															Open ↗
														</Link>
													)}
												</div>
											</div>
										))}
									</div>
								</div>

								<div className="lg:col-span-2 rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-6 shadow-sm flex flex-col min-h-[320px]">
									<h2 className="font-heading text-[20px] text-text-primary mb-4">Recent activity</h2>
									<div className="flex-1 space-y-0 overflow-y-auto max-h-[420px] pr-1">
										{dash.recent_submissions.length === 0 ? (
											<p className="text-[13px] text-text-tertiary py-8 text-center">No submissions yet.</p>
										) : (
											dash.recent_submissions.map((row, i) => (
												<div
													key={row.submission_id}
													className={`flex gap-3 py-3 ${i > 0 ? "border-t border-stone-100" : ""}`}
												>
													<span className="mt-1.5 w-2 h-2 rounded-full bg-forest-400 flex-shrink-0" />
													<div className="min-w-0 flex-1">
														<p className="text-[11px] text-text-tertiary font-medium uppercase tracking-wide">
															{formatRelativeShort(row.completed_at)}
														</p>
														<p className="text-[13px] text-text-primary mt-0.5">
															New response on{" "}
															<Link
																to={`/admin/forms/${row.form_id}/submissions`}
																className="text-forest-600 hover:underline font-medium"
															>
																{row.form_title}
															</Link>
														</p>
													</div>
												</div>
											))
										)}
									</div>
									<div className="mt-6 pt-5 border-t border-stone-100 flex items-center gap-3">
										<div className="w-10 h-10 rounded-full bg-forest-100 text-forest-700 grid place-items-center text-[14px] font-heading font-semibold">
											{(admin?.full_name ?? admin?.email ?? "?").charAt(0).toUpperCase()}
										</div>
										<div className="min-w-0">
											<p className="text-[14px] font-medium text-text-primary truncate">
												{admin?.full_name || "Admin"}
											</p>
											<p className="text-[11px] text-text-tertiary uppercase tracking-wider truncate">
												{admin?.email}
											</p>
										</div>
									</div>
								</div>
							</section>

							<footer className="pt-6 border-t border-stone-200 flex flex-wrap gap-x-6 gap-y-2 text-[11px] text-text-tertiary uppercase tracking-wider">
								<span>Workspace analytics · sessions &amp; completions</span>
							</footer>
						</>
					)}
				</div>
			</PageBody>
		</AdminShell>
	);
}

function StatusBadge({ status }: { status: string }) {
	if (status === "published") {
		return (
			<span className="inline-flex items-center gap-1 px-2.5 py-[2px] rounded-full text-[11px] font-medium bg-forest-100 text-forest-600">
				<span className="w-[6px] h-[6px] rounded-full bg-forest-500 animate-pulse-dot" />
				active
			</span>
		);
	}
	if (status === "draft") {
		return (
			<span className="inline-flex items-center px-2.5 py-[2px] rounded-full text-[11px] font-medium bg-stone-200/80 text-stone-600">
				draft
			</span>
		);
	}
	return (
		<span className="inline-flex items-center px-2.5 py-[2px] rounded-full text-[11px] font-medium bg-stone-100 text-stone-500">
			{status}
		</span>
	);
}
