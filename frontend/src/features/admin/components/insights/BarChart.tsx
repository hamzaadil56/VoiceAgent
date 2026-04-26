import type { FieldValueCount } from "../../../../shared/types/api";

export function BarChart({ values, label }: { values: FieldValueCount[]; label: string }) {
	const w = 720;
	const h = 160;
	const pad = { t: 12, r: 8, b: 36, l: 8 };
	const innerW = w - pad.l - pad.r;
	const innerH = h - pad.t - pad.b;

	const maxCount = Math.max(1, ...values.map((v) => v.count));
	const barCount = values.length;
	const barW = Math.max(8, Math.floor(innerW / barCount) - 4);
	const gap = barCount > 1 ? (innerW - barW * barCount) / (barCount - 1) : 0;

	return (
		<div>
			<p className="text-[11px] text-text-tertiary uppercase tracking-wider mb-2">{label}</p>
			<svg viewBox={`0 0 ${w} ${h}`} className="w-full h-[160px]" preserveAspectRatio="none">
				{values.map((v, i) => {
					const barH = Math.max(2, Math.round((v.count / maxCount) * innerH));
					const x = pad.l + i * (barW + gap);
					const y = pad.t + innerH - barH;
					return (
						<g key={`${v.value}-${i}`}>
							<rect
								x={x} y={y} width={barW} height={barH}
								rx={3} fill="rgb(45, 106, 90)" fillOpacity={0.8}
							/>
							<text
								x={x + barW / 2} y={h - pad.b + 14}
								textAnchor="middle"
								fontFamily="system-ui"
								fontSize={barCount > 6 ? 9 : 10}
								fill="rgb(120,113,108)"
							>
								{v.value.length > 10 ? v.value.slice(0, 9) + "…" : v.value}
							</text>
							<text
								x={x + barW / 2} y={y - 3}
								textAnchor="middle"
								fontFamily="system-ui"
								fontSize={10}
								fill="rgb(68,64,60)"
							>
								{v.count}
							</text>
						</g>
					);
				})}
			</svg>
		</div>
	);
}
