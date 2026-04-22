import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../../app/AuthProvider";
import { createForm, fetchTemplates } from "../api/adminApi";
import { AdminShell, PageBody, PageHeader } from "../../../shared/ui/Layout";
import type { FormTemplate } from "../../../shared/types/api";

const CATEGORIES = [
	{ key: "all", label: "All" },
	{ key: "feedback", label: "Feedback" },
	{ key: "hr", label: "HR" },
	{ key: "sales", label: "Sales" },
	{ key: "support", label: "Support" },
	{ key: "events", label: "Events" },
	{ key: "general", label: "General" },
	{ key: "education", label: "Education" },
	{ key: "healthcare", label: "Healthcare" },
	{ key: "marketing", label: "Marketing" },
	{ key: "research", label: "Research" },
];

export default function TemplatesPage() {
	const { admin, logout } = useAuth();
	const navigate = useNavigate();
	const orgId = admin?.memberships[0]?.org_id;

	const [templates, setTemplates] = useState<FormTemplate[]>([]);
	const [loading, setLoading] = useState(true);
	const [category, setCategory] = useState("all");
	const [creating, setCreating] = useState<string | null>(null);

	useEffect(() => {
		fetchTemplates()
			.then(setTemplates)
			.catch(() => {})
			.finally(() => setLoading(false));
	}, []);

	const filtered =
		category === "all"
			? templates
			: templates.filter((t) => t.category === category);

	const handleUseTemplate = async (template: FormTemplate) => {
		if (!orgId) return;
		setCreating(template.id);
		try {
			const slug =
				template.id +
				`-${Math.floor(Math.random() * 10000)}`;
			const form = await createForm(orgId, {
				title: template.title,
				description: template.description,
				slug,
				mode: template.mode as "chat" | "voice" | "chat_voice",
				persona: template.persona,
				system_prompt: template.system_prompt,
				fields: template.fields,
			});
			navigate(`/admin/forms/${form.id}`);
		} catch {
			setCreating(null);
		}
	};

	return (
		<AdminShell
			email={admin?.email}
			onLogout={() => {
				logout();
				navigate("/admin/login");
			}}
		>
			<PageHeader
				title="Templates"
				subtitle="Start from a pre-built template and customize it."
				backTo="/admin"
				backLabel="Dashboard"
			/>
			<PageBody>
				{/* Category filter */}
				<div className="flex flex-wrap gap-2 mb-6">
					{CATEGORIES.map((cat) => (
						<button
							key={cat.key}
							type="button"
							onClick={() => setCategory(cat.key)}
							className={`px-3.5 py-1.5 rounded-full text-[12px] font-medium transition-all ${
								category === cat.key
									? "bg-forest-500 text-white shadow-forest"
									: "bg-stone-100 text-text-secondary hover:bg-stone-200 hover:text-text-primary"
							}`}
						>
							{cat.label}
						</button>
					))}
				</div>

				{loading ? (
					<div className="flex justify-center py-20">
						<div className="w-6 h-6 border-2 border-forest-500 border-t-transparent rounded-full animate-spin" />
					</div>
				) : (
					<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
						{filtered.map((t) => (
							<div
								key={t.id}
								className="rounded-xl border-[0.5px] border-stone-200 bg-bg-base p-5 shadow-sm hover:shadow-md hover:border-forest-200/80 transition-all group"
							>
								<div className="flex items-start justify-between mb-3">
									<div>
										<h3 className="font-heading font-medium text-[16px] text-text-primary">
											{t.title}
										</h3>
										<span className="text-[11px] uppercase tracking-wide text-text-tertiary">
											{t.category} ·{" "}
											{t.mode.replace("_", " + ")}
										</span>
									</div>
									<span className="text-[11px] px-2 py-0.5 rounded-full bg-stone-100 text-text-tertiary">
										{t.fields.length} fields
									</span>
								</div>
								<p className="text-[13px] text-text-secondary mb-4 line-clamp-2">
									{t.description}
								</p>
								<div className="flex flex-wrap gap-1.5 mb-4">
									{t.fields.slice(0, 4).map((f) => (
										<span
											key={f.name}
											className="text-[11px] px-2 py-0.5 rounded bg-stone-50 text-text-tertiary font-mono"
										>
											{f.name}
										</span>
									))}
									{t.fields.length > 4 && (
										<span className="text-[11px] px-2 py-0.5 rounded bg-stone-50 text-text-tertiary">
											+{t.fields.length - 4} more
										</span>
									)}
								</div>
								<button
									type="button"
									onClick={() => handleUseTemplate(t)}
									disabled={creating === t.id}
									className="w-full px-4 py-[9px] rounded-md text-[13px] font-medium text-forest-600 bg-forest-50 border-[0.5px] border-forest-200 hover:bg-forest-100 transition-all disabled:opacity-50"
								>
									{creating === t.id
										? "Creating..."
										: "Use Template"}
								</button>
							</div>
						))}
					</div>
				)}
			</PageBody>
		</AdminShell>
	);
}
