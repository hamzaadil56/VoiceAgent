import { type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../../app/AuthProvider";
import { createForm, generateForm, publishForm } from "../api/adminApi";
import { PromptFormBuilder } from "../components/PromptFormBuilder";
import { AdminShell, PageBody, PageHeader } from "../../../shared/ui/Layout";
import type {
	FormCreatePayload,
	FormCreateResponse,
	FormField,
} from "../../../shared/types/api";

export default function FormEditorPage() {
	const { admin, logout } = useAuth();
	const navigate = useNavigate();
	const orgId = admin?.memberships[0]?.org_id;

	const [prompt, setPrompt] = useState("");
	const [isGenerating, setIsGenerating] = useState(false);

	const [title, setTitle] = useState("");
	const [description, setDescription] = useState("");
	const [slug, setSlug] = useState("");
	const [mode, setMode] = useState<"chat" | "voice" | "chat_voice">("chat_voice");
	const [persona, setPersona] = useState("Friendly and professional");
	const [systemPrompt, setSystemPrompt] = useState("");
	const [fields, setFields] = useState<FormField[]>([]);

	const [createdForm, setCreatedForm] = useState<FormCreateResponse | null>(null);
	const [status, setStatus] = useState("");
	const [saving, setSaving] = useState(false);

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
			setSlug(
				result.title
					.toLowerCase()
					.replace(/[^a-z0-9]+/g, "-")
					.replace(/^-|-$/g, "") +
					`-${Math.floor(Math.random() * 1000)}`,
			);
			setStatus("Form generated successfully! Review and save below.");
		} catch (err) {
			setStatus(err instanceof Error ? err.message : "Failed to generate form");
		} finally {
			setIsGenerating(false);
		}
	};

	const handleCreate = async (event: FormEvent) => {
		event.preventDefault();
		if (!orgId) { setStatus("No workspace found"); return; }
		if (!systemPrompt && fields.length === 0) { setStatus("Generate a form first, or add fields manually"); return; }
		setSaving(true);
		setStatus("Creating form...");
		try {
			const payload: FormCreatePayload = { title, description, slug, mode, persona, system_prompt: systemPrompt, fields };
			const form = await createForm(orgId, payload);
			setCreatedForm(form);
			setStatus("Form created successfully!");
		} catch (err) {
			setStatus(err instanceof Error ? err.message : "Failed to create form");
		} finally {
			setSaving(false);
		}
	};

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
		<AdminShell email={admin?.email} onLogout={() => { logout(); navigate("/admin/login"); }}>
			<PageHeader
				title={createdForm ? "Form Created" : "Create Form"}
				subtitle="Describe what you want to collect and let AI build the form."
				backTo="/admin"
				backLabel="Dashboard"
			/>
			<PageBody>
				<form onSubmit={handleCreate} className="space-y-6 max-w-3xl">
					<PromptFormBuilder
						prompt={prompt}
						onPromptChange={setPrompt}
						fields={fields}
						onFieldsChange={setFields}
						onGenerate={handleGenerate}
						isGenerating={isGenerating}
					/>

					{/* Form Settings */}
					<section className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 p-6 space-y-4">
						<h2 className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary">
							Form Settings
						</h2>
						<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
							<FieldInput label="Title" id="title" value={title} onChange={setTitle} placeholder="Form title" required />
							<FieldInput label="URL Slug" id="slug" value={slug} onChange={setSlug} placeholder="my-form" required mono />
						</div>
						<div>
							<label htmlFor="description" className="block text-[13px] font-medium text-text-primary mb-[5px]">
								Description
							</label>
							<textarea
								id="description"
								className="w-full px-3 py-[9px] rounded-md text-sm text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all placeholder:text-text-tertiary focus:border-forest-500 focus:shadow-forest-ring resize-none"
								value={description}
								onChange={(e) => setDescription(e.target.value)}
								placeholder="Describe what this form collects"
								rows={2}
							/>
						</div>
						<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
							<div>
								<label htmlFor="mode" className="block text-[13px] font-medium text-text-primary mb-[5px]">
									Mode
								</label>
								<select
									id="mode"
									className="w-full px-3 py-[9px] rounded-md text-sm text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all focus:border-forest-500 focus:shadow-forest-ring"
									value={mode}
									onChange={(e) => setMode(e.target.value as typeof mode)}
								>
									<option value="chat">Chat only</option>
									<option value="voice">Voice only</option>
									<option value="chat_voice">Chat + Voice</option>
								</select>
							</div>
							<FieldInput label="Bot Persona" id="persona" value={persona} onChange={setPersona} placeholder="Friendly and professional" />
						</div>
						<div>
							<label htmlFor="system-prompt" className="block text-[13px] font-medium text-text-primary mb-[5px]">
								Agent Instructions{" "}
								<span className="text-text-tertiary font-normal">(auto-generated, editable)</span>
							</label>
							<textarea
								id="system-prompt"
								className="w-full px-3 py-[9px] rounded-md text-[13px] font-mono text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all placeholder:text-text-tertiary focus:border-forest-500 focus:shadow-forest-ring resize-none"
								value={systemPrompt}
								onChange={(e) => setSystemPrompt(e.target.value)}
								placeholder="Instructions for the conversational agent..."
								rows={4}
							/>
						</div>
					</section>

					{/* Fields Summary */}
					{fields.length > 0 && (
						<section className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 p-6">
							<h2 className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary mb-3">
								Fields ({fields.length})
							</h2>
							<div className="space-y-2 text-[13px]">
								{fields.map((field, i) => (
									<div key={field.name} className="flex items-center gap-3">
										<span className="text-text-tertiary w-5 text-right">{i + 1}.</span>
										<span className="font-mono text-forest-600">{field.name}</span>
										<span className="text-[11px] px-2 py-0.5 rounded bg-stone-50 text-text-tertiary">
											{field.type}
										</span>
										{field.required && <span className="text-[11px] text-warning">required</span>}
										{field.description && <span className="text-text-secondary text-[11px] truncate max-w-[200px]">{field.description}</span>}
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
								disabled={saving || (!systemPrompt && fields.length === 0)}
								className="px-6 py-[9px] rounded-md font-medium text-[13px] text-white bg-forest-500 hover:bg-forest-600 transition-all duration-150 disabled:opacity-50 shadow-forest"
							>
								{saving ? "Creating..." : "Create Draft Form"}
							</button>
						) : (
							<>
								<button
									type="button"
									onClick={handlePublish}
									disabled={saving}
									className="px-6 py-[9px] rounded-md font-medium text-[13px] text-white bg-clay-500 hover:bg-clay-600 transition-all duration-150 disabled:opacity-50 shadow-clay"
								>
									{saving ? "Publishing..." : "Publish Form"}
								</button>
								<Link
									to={`/f/${createdForm.slug}`}
									target="_blank"
									className="px-6 py-[9px] rounded-md text-[13px] text-text-secondary bg-bg-base border-[0.5px] border-stone-200 hover:border-stone-300 hover:text-text-primary transition-all inline-flex items-center"
								>
									Preview ↗
								</Link>
								<Link
									to={`/admin/forms/${createdForm.id}/submissions`}
									className="px-6 py-[9px] rounded-md text-[13px] text-text-secondary bg-bg-base border-[0.5px] border-stone-200 hover:border-stone-300 hover:text-text-primary transition-all inline-flex items-center"
								>
									Submissions
								</Link>
							</>
						)}
						<button
							type="button"
							onClick={() => navigate("/admin")}
							className="px-6 py-[9px] rounded-md text-[13px] text-text-secondary bg-bg-base border-[0.5px] border-stone-200 hover:border-stone-300 hover:text-text-primary transition-all"
						>
							Cancel
						</button>
					</div>
				</form>

				{status && (
					<div
						className="mt-6 rounded-md p-4 border-[0.5px] text-[13px]"
						style={
							status.includes("fail") || status.includes("error")
								? { borderColor: "var(--error-border)", color: "var(--color-error)", background: "var(--error-bg)" }
								: { borderColor: "var(--border-subtle)", color: "var(--text-secondary)", background: "var(--stone-50)" }
						}
					>
						{status}
					</div>
				)}
			</PageBody>
		</AdminShell>
	);
}

function FieldInput({
	label, id, value, onChange, placeholder, required, mono,
}: {
	label: string; id: string; value: string; onChange: (v: string) => void;
	placeholder: string; required?: boolean; mono?: boolean;
}) {
	return (
		<div>
			<label htmlFor={id} className="block text-[13px] font-medium text-text-primary mb-[5px]">
				{label}
			</label>
			<input
				id={id}
				className={`w-full px-3 py-[9px] rounded-md text-sm text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all placeholder:text-text-tertiary focus:border-forest-500 focus:shadow-forest-ring${mono ? " font-mono text-[13px]" : ""}`}
				value={value}
				onChange={(e) => onChange(e.target.value)}
				placeholder={placeholder}
				required={required}
			/>
		</div>
	);
}
