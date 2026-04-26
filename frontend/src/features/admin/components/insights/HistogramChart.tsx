import type { FieldNumericStats } from "../../../../shared/types/api";

function fmt(v: number | null): string {
	if (v === null) return "—";
	return v === Math.floor(v) ? String(v) : v.toFixed(2);
}

export function HistogramChart({ stats }: { stats: FieldNumericStats }) {
	const w = 720;
	const h = 140;
	const pad = { t: 12, r: 8, b: 36, l: 8 };
	const innerW = w - pad.l - pad.r;
	const innerH = h - pad.t - pad.b;

	const buckets = stats.histogram;
	const maxCount = Math.max(1, ...buckets.map((b) => b.count));
	const barW = Math.max(8, Math.floor(innerW / buckets.length) - 4);
	const gap = buckets.length > 1 ? (innerW - barW * buckets.length) / (buckets.length - 1) : 0;

	return (
		<div>
			{stats.parseable_count < stats.count && (
				<p className="text-[11px] text-text-tertiary mb-1">
					{stats.parseable_count} of {stats.count} responses parseable as numbers
				</p>
			)}
			<svg viewBox={`0 0 ${w} ${h}`} className="w-full h-[140px]" preserveAspectRatio="none">
				{buckets.map((b, i) => {
					const barH = Math.max(2, Math.round((b.count / maxCount) * innerH));
					const x = pad.l + i * (barW + gap);
					const y = pad.t + innerH - barH;
					return (
						<g key={`${b.bucket_label}-${i}`}>
							<rect
								x={x} y={y} width={barW} height={barH}
								rx={2} fill="rgb(45, 106, 90)" fillOpacity={0.75}
							/>
							<text
								x={x + barW / 2} y={h - pad.b + 14}
								textAnchor="middle"
								fontFamily="system-ui"
								fontSize={9}
								fill="rgb(120,113,108)"
							>
								{b.bucket_label}
							</text>
							{b.count > 0 && (
								<text
									x={x + barW / 2} y={y - 3}
									textAnchor="middle"
									fontFamily="system-ui"
									fontSize={10}
									fill="rgb(68,64,60)"
								>
									{b.count}
								</text>
							)}
						</g>
					);
				})}
			</svg>
			<div className="flex gap-6 text-[12px] text-text-secondary mt-1">
				<span>Min: <strong>{fmt(stats.min_val)}</strong></span>
				<span>Max: <strong>{fmt(stats.max_val)}</strong></span>
				<span>Avg: <strong>{fmt(stats.avg_val)}</strong></span>
				<span>Median: <strong>{fmt(stats.median_val)}</strong></span>
			</div>
		</div>
	);
}
