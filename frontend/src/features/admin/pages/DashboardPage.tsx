import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../../app/AuthProvider";
import { adminApi } from "../../../shared/lib/httpClient";
import type { FormSummary } from "../../../shared/types/api";

export default function DashboardPage() {
	const { admin, logout } = useAuth();
	const navigate = useNavigate();
	const [forms, setForms] = useState<FormSummary[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	const orgId = admin?.memberships[0]?.org_id;

	useEffect(() => {
		if (!orgId) return;
		setLoading(true);
		adminApi
			.get<{ forms: FormSummary[] }>(`/orgs/${orgId}/forms`)
			.then((res) => setForms(res.forms))
			.catch((err) => {
				// If the list endpoint doesn't exist yet, show empty state
				if (err.status === 404 || err.status === 405) {
					setForms([]);
				} else {
					setError(err.message);
				}
			})
			.finally(() => setLoading(false));
	}, [orgId]);

	const handleLogout = () => {
		logout();
		navigate("/admin/login");
	};

	return (
		<div className="max-w-6xl mx-auto py-8 px-4 space-y-6">
			{/* Header */}
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-heading font-bold text-text-primary">
						Agentic Forms
					</h1>
					<p className="text-text-secondary text-sm mt-1">
						{admin?.email}
					</p>
				</div>
				<div className="flex gap-3">
					<Link
						to="/admin/forms/new"
						className="px-5 py-2.5 rounded-xl bg-accent-primary text-bg-primary font-semibold hover:opacity-90"
					>
						Create Form
					</Link>
					<button
						onClick={handleLogout}
						className="px-4 py-2.5 rounded-xl glass border border-border text-text-secondary hover:text-text-primary hover:border-border-hover"
					>
						Logout
					</button>
				</div>
			</div>

			{/* Form List */}
			{loading ? (
				<div className="flex justify-center py-20">
					<div className="w-8 h-8 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
				</div>
			) : error ? (
				<div className="glass-elevated rounded-2xl p-8 border border-error/30 text-center">
					<p className="text-error">{error}</p>
				</div>
			) : forms.length === 0 ? (
				<div className="glass-elevated rounded-2xl p-12 border border-border/40 text-center">
					<h2 className="text-xl font-heading text-text-primary mb-2">
						No forms yet
					</h2>
					<p className="text-text-secondary mb-6">
						Create your first conversational form to get started.
					</p>
					<Link
						to="/admin/forms/new"
						className="inline-block px-6 py-3 rounded-xl bg-accent-primary text-bg-primary font-semibold hover:opacity-90"
					>
						Create Your First Form
					</Link>
				</div>
			) : (
				<div className="grid gap-4">
					{forms.map((form) => (
						<div
							key={form.id}
							className="glass rounded-2xl p-6 border border-border/40 hover:border-border-hover flex items-center justify-between"
						>
							<div className="flex-1 min-w-0">
								<div className="flex items-center gap-3 mb-1">
									<h3 className="text-lg font-heading text-text-primary truncate">
										{form.title}
									</h3>
									<span
										className={`text-xs px-2 py-0.5 rounded-full ${
											form.status === "published"
												? "bg-success/20 text-success"
												: "bg-warning/20 text-warning"
										}`}
									>
										{form.status}
									</span>
								</div>
								<p className="text-sm text-text-tertiary">
									/{form.slug} &middot; {form.mode}
								</p>
							</div>
							<div className="flex gap-2 ml-4">
								<Link
									to={`/admin/forms/${form.id}`}
									className="px-3 py-2 rounded-lg glass border border-border text-sm text-text-secondary hover:text-text-primary"
								>
									Edit
								</Link>
								<Link
									to={`/admin/forms/${form.id}/submissions`}
									className="px-3 py-2 rounded-lg glass border border-border text-sm text-text-secondary hover:text-text-primary"
								>
									Submissions
								</Link>
								{form.status === "published" && (
									<Link
										to={`/f/${form.slug}`}
										target="_blank"
										className="px-3 py-2 rounded-lg bg-accent-primary/10 text-accent-primary text-sm"
									>
										Open
									</Link>
								)}
							</div>
						</div>
					))}
				</div>
			)}
		</div>
	);
}
