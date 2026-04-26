import type {
	FieldAIInsight,
	FieldCategoricalStats,
	FieldDistribution,
	FieldNumericStats,
	FieldTextStats,
} from "../../../../shared/types/api";
import { AIInsightPanel } from "./AIInsightPanel";
import { BarChart } from "./BarChart";
import { HistogramChart } from "./HistogramChart";
import { TopValuesList } from "./TopValuesList";

const TYPE_LABELS: Record<string, string> = {
	text: "Text",
	email: "Email",
	number: "Number",
	phone: "Phone",
	url: "URL",
	date: "Date",
	select: "Select",
	boolean: "Yes / No",
};

function FieldChart({ dist }: { dist: FieldDistribution }) {
	const { field_type, stats } = dist;

	if (field_type === "number") {
		const s = stats as FieldNumericStats;
		if (!s.parseable_count) {
			return <p className="text-[13px] text-text-tertiary">No numeric responses yet.</p>;
		}
		return <HistogramChart stats={s} />;
	}

	if (field_type === "select" || field_type === "boolean") {
		const s = stats as FieldCategoricalStats;
		if (!s.value_counts.length) {
			return <p className="text-[13px] text-text-tertiary">No responses yet.</p>;
		}
		return <BarChart values={s.value_counts} label={`${s.total_responses} total responses`} />;
	}

	// text / email / phone / url / date
	const s = stats as FieldTextStats;
	return <TopValuesList values={s.top_values} total={s.total_responses} />;
}

export function FieldDistributionCard({
	dist,
	aiInsight,
}: {
	dist: FieldDistribution;
	aiInsight?: FieldAIInsight;
}) {
	const typeBadge = TYPE_LABELS[dist.field_type] ?? dist.field_type;

	return (
		<div className="rounded-xl border border-stone-200 bg-white shadow-sm p-5">
			<div className="flex items-center gap-2 mb-4">
				<h3 className="text-[14px] font-semibold text-text-primary">{dist.field_name}</h3>
				<span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-stone-100 text-stone-500 uppercase tracking-wider">
					{typeBadge}
				</span>
			</div>

			<div className={`${aiInsight ? "grid grid-cols-1 lg:grid-cols-5 gap-5" : ""}`}>
				<div className={aiInsight ? "lg:col-span-3" : ""}>
					<FieldChart dist={dist} />
				</div>
				{aiInsight && (
					<div className="lg:col-span-2">
						<AIInsightPanel insight={aiInsight} />
					</div>
				)}
			</div>
		</div>
	);
}
