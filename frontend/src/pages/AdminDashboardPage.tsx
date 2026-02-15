import { FormEvent, useEffect, useMemo, useState } from "react";
import {
	clearAdminToken,
	createForm,
	exportCsv,
	fetchMe,
	fetchSubmissions,
	GraphEdgeIn,
	GraphNodeIn,
	getAdminToken,
	publishForm,
} from "../lib/agenticApi";

type CreatedForm = { id: string; slug: string; version_id: string; status: string };

const starterNodes: GraphNodeIn[] = [
	{ key: "full_name", prompt: "What is your full name?", node_type: "question", required: true, validation: {} },
	{ key: "email", prompt: "What is your email address?", node_type: "question", required: true, validation: { regex: "^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$" } },
	{ key: "goal", prompt: "What are you looking to achieve?", node_type: "question", required: true, validation: {} },
] ;

const starterEdges: GraphEdgeIn[] = [
	{ from_key: "full_name", to_key: "email" },
	{ from_key: "email", to_key: "goal" },
	{ from_key: "goal", to_key: null },
];

export default function AdminDashboardPage() {
	const token = getAdminToken();
	const [orgId, setOrgId] = useState<string>("");
	const [createdForm, setCreatedForm] = useState<CreatedForm | null>(null);
	const [formIdForData, setFormIdForData] = useState("");
	const [submissions, setSubmissions] = useState<Array<{ submission_id: string; answers: Record<string, string> }>>([]);
	const [status, setStatus] = useState<string>("");

	const [title, setTitle] = useState("Lead Qualification Form");
	const [description, setDescription] = useState("Conversational lead intake form");
	const [slug, setSlug] = useState(`lead-intake-${Math.floor(Math.random() * 1000)}`);
	const [persona, setPersona] = useState("Friendly, concise, and professional");

	useEffect(() => {
		if (!token) return;
		fetchMe(token)
			.then((me) => {
				const membership = me.memberships[0];
				if (membership) setOrgId(membership.org_id);
			})
			.catch((err) => setStatus(err.message));
	}, [token]);

	const consumerLink = useMemo(() => {
		if (!createdForm?.slug) return "";
		return `${window.location.origin}/f/${createdForm.slug}`;
	}, [createdForm]);

	if (!token) {
		return <div className="max-w-xl mx-auto mt-20 text-center text-text-primary">Please login at <code>/admin/login</code>.</div>;
	}

	const handleCreate = async (event: FormEvent) => {
		event.preventDefault();
		if (!orgId) {
			setStatus("No workspace found for this user.");
			return;
		}
		setStatus("Creating form...");
		try {
			const form = await createForm(token, orgId, {
				title,
				description,
				slug,
				mode: "chat_voice",
				persona,
				start_node_key: "full_name",
				graph_nodes: starterNodes,
				graph_edges: starterEdges,
			});
			setCreatedForm(form);
			setFormIdForData(form.id);
			setStatus(`Form created: ${form.id}`);
		} catch (err) {
			setStatus(err instanceof Error ? err.message : "Failed to create form");
		}
	};

	const handlePublish = async () => {
		if (!createdForm) return;
		setStatus("Publishing form...");
		try {
			const result = await publishForm(token, createdForm.id);
			setStatus(`Published version ${result.published_version_id}`);
		} catch (err) {
			setStatus(err instanceof Error ? err.message : "Publish failed");
		}
	};

	const handleFetchSubmissions = async () => {
		if (!formIdForData) return;
		setStatus("Loading submissions...");
		try {
			const result = await fetchSubmissions(token, formIdForData);
			setSubmissions(result.rows);
			setStatus(`Loaded ${result.total} submissions`);
		} catch (err) {
			setStatus(err instanceof Error ? err.message : "Failed loading submissions");
		}
	};

	const handleExport = async () => {
		if (!formIdForData) return;
		setStatus("Exporting CSV...");
		try {
			const result = await exportCsv(token, formIdForData);
			setStatus(`Export ${result.export_id} created (${result.row_count} rows). ${result.file_path || ""}`);
		} catch (err) {
			setStatus(err instanceof Error ? err.message : "Export failed");
		}
	};

	return (
		<div className="max-w-5xl mx-auto py-8 px-4 space-y-6">
			<div className="flex items-center justify-between">
				<h1 className="text-3xl font-heading text-text-primary">Agentic Forms Admin</h1>
				<button onClick={() => { clearAdminToken(); window.location.href = "/admin/login"; }} className="px-4 py-2 rounded-lg glass border border-border">Logout</button>
			</div>

			<form onSubmit={handleCreate} className="glass-elevated rounded-2xl p-6 border border-border/40 space-y-4">
				<h2 className="text-xl font-heading text-text-primary">Create Form</h2>
				<input className="w-full px-4 py-3 glass rounded-xl border border-border" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Title" />
				<input className="w-full px-4 py-3 glass rounded-xl border border-border" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" />
				<input className="w-full px-4 py-3 glass rounded-xl border border-border" value={slug} onChange={(e) => setSlug(e.target.value)} placeholder="slug" />
				<input className="w-full px-4 py-3 glass rounded-xl border border-border" value={persona} onChange={(e) => setPersona(e.target.value)} placeholder="Persona" />
				<button className="px-5 py-3 rounded-xl bg-accent-primary text-bg-primary font-semibold" type="submit">Create Draft Form</button>
			</form>

			{createdForm && (
				<div className="glass rounded-2xl p-6 border border-border/40 space-y-3">
					<p className="text-text-primary">Form ID: <code>{createdForm.id}</code></p>
					<p className="text-text-primary">Slug: <code>{createdForm.slug}</code></p>
					<button onClick={handlePublish} className="px-5 py-3 rounded-xl bg-accent-secondary text-bg-primary font-semibold">Publish Form</button>
					{consumerLink && <p className="text-text-secondary">Consumer Link: <a className="text-accent-primary underline" href={consumerLink}>{consumerLink}</a></p>}
				</div>
			)}

			<div className="glass rounded-2xl p-6 border border-border/40 space-y-3">
				<h2 className="text-xl font-heading text-text-primary">Submissions & Export</h2>
				<input className="w-full px-4 py-3 glass rounded-xl border border-border" value={formIdForData} onChange={(e) => setFormIdForData(e.target.value)} placeholder="Form ID" />
				<div className="flex gap-3">
					<button onClick={handleFetchSubmissions} className="px-4 py-2 rounded-lg bg-surface text-text-primary">Load Submissions</button>
					<button onClick={handleExport} className="px-4 py-2 rounded-lg bg-surface text-text-primary">Export CSV</button>
				</div>
				{submissions.length > 0 && (
					<div className="max-h-64 overflow-auto text-sm text-text-secondary">
						<pre>{JSON.stringify(submissions, null, 2)}</pre>
					</div>
				)}
			</div>

			{status && <p className="text-text-secondary">{status}</p>}
		</div>
	);
}
