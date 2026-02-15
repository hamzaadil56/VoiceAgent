/** Form editor page — create agentic forms with AI-powered prompt builder */
import { type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../../app/AuthProvider";
import { createForm, generateForm, publishForm } from "../api/adminApi";
import { PromptFormBuilder } from "../components/PromptFormBuilder";
import type {
	FormCreatePayload,
	FormCreateResponse,
	FormField,
} from "../../../shared/types/api";

export default function FormEditorPage() {
	const { admin } = useAuth();
	const navigate = useNavigate();
	const orgId = admin?.memberships[0]?.org_id;

	// AI prompt
	const [prompt, setPrompt] = useState("");
	const [isGenerating, setIsGenerating] = useState(false);

	// Form metadata
	const [title, setTitle] = useState("");
	const [description, setDescription] = useState("");
	const [slug, setSlug] = useState("");
	const [mode, setMode] = useState<"chat" | "voice" | "chat_voice">("chat_voice");
	const [persona, setPersona] = useState("Friendly and professional");
	const [systemPrompt, setSystemPrompt] = useState("");

	// Fields
	const [fields, setFields] = useState<FormField[]>([]);

	// State
	const [createdForm, setCreatedForm] = useState<FormCreateResponse | null>(
		null,
	);
	const [status, setStatus] = useState("");
	const [saving, setSaving] = useState(false);

	// --- AI Generation ---
	const handleGenerate = async () => {
		if (!orgId || prompt.trim().length < 10) return;
		setIsGenerating(true);
		setStatus("Generating form with AI...");
		try {
			const result = await generateForm(orgId, prompt);
			setTitle(result.title);
			setDescription(result.description);
			setSystemPrompt(result.system_prompt);
			setFields(result.fields);
			// Auto-generate slug from title
			setSlug(
				result.title
					.toLowerCase()
					.replace(/[^a-z0-9]+/g, "-")
					.replace(/^-|-$/g, "") +
					`-${Math.floor(Math.random() * 1000)}`,
			);
			setStatus("Form generated successfully! Review and save below.");
		} catch (err) {
			setStatus(
				err instanceof Error ? err.message : "Failed to generate form",
			);
		} finally {
			setIsGenerating(false);
		}
	};

	// --- Create form ---
	const handleCreate = async (event: FormEvent) => {
		event.preventDefault();
		if (!orgId) {
			setStatus("No workspace found");
			return;
		}
		if (!systemPrompt && fields.length === 0) {
			setStatus("Generate a form first, or add fields manually");
			return;
		}
		setSaving(true);
		setStatus("Creating form...");
		try {
			const payload: FormCreatePayload = {
				title,
				description,
				slug,
				mode,
				persona,
				system_prompt: systemPrompt,
				fields,
			};
			const form = await createForm(orgId, payload);
			setCreatedForm(form);
			setStatus("Form created successfully!");
		} catch (err) {
			setStatus(
				err instanceof Error ? err.message : "Failed to create form",
			);
		} finally {
			setSaving(false);
		}
	};

	// --- Publish ---
	const handlePublish = async () => {
		if (!createdForm) return;
		setSaving(true);
		setStatus("Publishing form...");
		try {
			await publishForm(createdForm.id);
			setStatus("Form published! Consumers can now access it.");
		} catch (err) {
			setStatus(err instanceof Error ? err.message : "Publish failed");
		} finally {
			setSaving(false);
		}
	};

	return (
		<div className="max-w-4xl mx-auto py-8 px-4 space-y-6">
			{/* Header */}
			<div>
				<Link
					to="/admin"
					className="text-sm text-text-tertiary hover:text-accent-primary mb-2 inline-block"
				>
					&larr; Back to Dashboard
				</Link>
				<h1 className="text-2xl font-heading font-bold text-text-primary">
					{createdForm ? "Form Created" : "Create Agentic Form"}
				</h1>
				<p className="text-text-secondary mt-1">
					Describe what you want to collect and let AI build the form
					for you.
				</p>
			</div>

			<form onSubmit={handleCreate} className="space-y-6">
				{/* AI Prompt + Fields Builder */}
				<PromptFormBuilder
					prompt={prompt}
					onPromptChange={setPrompt}
					fields={fields}
					onFieldsChange={setFields}
					onGenerate={handleGenerate}
					isGenerating={isGenerating}
				/>

				{/* Form Metadata Section */}
				<section className="glass-elevated rounded-2xl p-6 border border-border/40 space-y-4">
					<h2 className="text-lg font-heading text-text-primary">
						Form Settings
					</h2>
					<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label
								htmlFor="title"
								className="block text-sm text-text-secondary mb-1"
							>
								Title
							</label>
							<input
								id="title"
								className="w-full px-4 py-3 glass rounded-xl border border-border text-text-primary focus:outline-none focus:border-accent-primary"
								value={title}
								onChange={(e) => setTitle(e.target.value)}
								placeholder="Form title"
								required
							/>
						</div>
						<div>
							<label
								htmlFor="slug"
								className="block text-sm text-text-secondary mb-1"
							>
								URL Slug
							</label>
							<input
								id="slug"
								className="w-full px-4 py-3 glass rounded-xl border border-border text-text-primary focus:outline-none focus:border-accent-primary"
								value={slug}
								onChange={(e) => setSlug(e.target.value)}
								placeholder="my-form"
								required
							/>
						</div>
					</div>
					<div>
						<label
							htmlFor="description"
							className="block text-sm text-text-secondary mb-1"
						>
							Description
						</label>
						<textarea
							id="description"
							className="w-full px-4 py-3 glass rounded-xl border border-border text-text-primary focus:outline-none focus:border-accent-primary resize-none"
							value={description}
							onChange={(e) => setDescription(e.target.value)}
							placeholder="Describe what this form collects"
							rows={2}
						/>
					</div>
					<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div>
							<label
								htmlFor="mode"
								className="block text-sm text-text-secondary mb-1"
							>
								Mode
							</label>
							<select
								id="mode"
								className="w-full px-4 py-3 glass rounded-xl border border-border text-text-primary focus:outline-none focus:border-accent-primary"
								value={mode}
								onChange={(e) =>
									setMode(e.target.value as typeof mode)
								}
							>
								<option value="chat">Chat only</option>
								<option value="voice">Voice only</option>
								<option value="chat_voice">Chat + Voice</option>
							</select>
						</div>
						<div>
							<label
								htmlFor="persona"
								className="block text-sm text-text-secondary mb-1"
							>
								Bot Persona
							</label>
							<input
								id="persona"
								className="w-full px-4 py-3 glass rounded-xl border border-border text-text-primary focus:outline-none focus:border-accent-primary"
								value={persona}
								onChange={(e) => setPersona(e.target.value)}
								placeholder="Friendly and professional"
							/>
						</div>
					</div>

					{/* System prompt (advanced, generated by AI) */}
					<div>
						<label
							htmlFor="system-prompt"
							className="block text-sm text-text-secondary mb-1"
						>
							Agent Instructions{" "}
							<span className="text-text-tertiary">
								(auto-generated by AI, editable)
							</span>
						</label>
						<textarea
							id="system-prompt"
							className="w-full px-4 py-3 glass rounded-xl border border-border text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-accent-primary resize-none font-mono text-sm"
							value={systemPrompt}
							onChange={(e) => setSystemPrompt(e.target.value)}
							placeholder="Instructions for the conversational agent..."
							rows={4}
						/>
					</div>
				</section>

				{/* Fields Summary */}
				{fields.length > 0 && (
					<section className="glass rounded-2xl p-6 border border-border/40">
						<h2 className="text-lg font-heading text-text-primary mb-3">
							Fields Summary
						</h2>
						<div className="space-y-2 text-sm">
							{fields.map((field, i) => (
								<div
									key={field.name}
									className="flex items-center gap-3"
								>
									<span className="text-text-tertiary w-6">
										{i + 1}.
									</span>
									<span className="text-accent-primary font-mono">
										{field.name}
									</span>
									<span className="text-text-tertiary px-2 py-0.5 rounded bg-surface/50 text-xs">
										{field.type}
									</span>
									{field.required && (
										<span className="text-xs text-warning">
											required
										</span>
									)}
									{field.description && (
										<span className="text-text-secondary text-xs truncate max-w-[200px]">
											{field.description}
										</span>
									)}
								</div>
							))}
						</div>
					</section>
				)}

				{/* Actions */}
				<div className="flex flex-wrap gap-3">
					{!createdForm ? (
						<button
							type="submit"
							disabled={
								saving || (!systemPrompt && fields.length === 0)
							}
							className="px-6 py-3 rounded-xl bg-accent-primary text-bg-primary font-semibold hover:opacity-90 disabled:opacity-50"
						>
							{saving ? "Creating..." : "Create Draft Form"}
						</button>
					) : (
						<>
							<button
								type="button"
								onClick={handlePublish}
								disabled={saving}
								className="px-6 py-3 rounded-xl bg-accent-secondary text-bg-primary font-semibold hover:opacity-90 disabled:opacity-50"
							>
								{saving ? "Publishing..." : "Publish Form"}
							</button>
							<Link
								to={`/f/${createdForm.slug}`}
								target="_blank"
								className="px-6 py-3 rounded-xl glass border border-border text-text-primary hover:border-border-hover inline-flex items-center"
							>
								Preview Consumer Link
							</Link>
							<Link
								to={`/admin/forms/${createdForm.id}/submissions`}
								className="px-6 py-3 rounded-xl glass border border-border text-text-secondary hover:text-text-primary inline-flex items-center"
							>
								View Submissions
							</Link>
						</>
					)}
					<button
						type="button"
						onClick={() => navigate("/admin")}
						className="px-6 py-3 rounded-xl glass border border-border text-text-secondary hover:text-text-primary"
					>
						Cancel
					</button>
				</div>
			</form>

			{/* Status */}
			{status && (
				<div
					className={`glass rounded-xl p-4 border ${
						status.includes("fail") || status.includes("error")
							? "border-error/30 text-error"
							: "border-border/40 text-text-secondary"
					}`}
				>
					{status}
				</div>
			)}
		</div>
	);
}
