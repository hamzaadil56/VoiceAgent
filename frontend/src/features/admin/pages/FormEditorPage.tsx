import { type FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../../app/AuthProvider";
import {
	createForm,
	duplicateForm,
	fetchForm,
	generateForm,
	publishForm,
	unpublishForm,
	updateForm,
} from "../api/adminApi";
import { PromptFormBuilder } from "../components/PromptFormBuilder";
import { AdminShell, PageBody, PageHeader } from "../../../shared/ui/Layout";
import { ShareModal } from "../components/ShareModal";
import type {
	FormBranding,
	FormCreatePayload,
	FormCreateResponse,
	FormField,
} from "../../../shared/types/api";

export default function FormEditorPage() {
	const { admin, logout } = useAuth();
	const navigate = useNavigate();
	const { formId } = useParams<{ formId: string }>();
	const orgId = admin?.memberships[0]?.org_id;

	const isEditMode = Boolean(formId);

	const [prompt, setPrompt] = useState("");
	const [isGenerating, setIsGenerating] = useState(false);
	const [loadingForm, setLoadingForm] = useState(false);

	const [title, setTitle] = useState("");
	const [description, setDescription] = useState("");
	const [slug, setSlug] = useState("");
	const [mode, setMode] = useState<"chat" | "voice" | "chat_voice">(
		"chat_voice",
	);
	const [persona, setPersona] = useState("Friendly and professional");
	const [systemPrompt, setSystemPrompt] = useState("");
	const [fields, setFields] = useState<FormField[]>([]);
	const [formStatus, setFormStatus] = useState<string>("draft");

	const [branding, setBranding] = useState<FormBranding>({
		logo_url: "",
		primary_color: "#2d6a5a",
		accent_color: "#c17c5a",
		font: "Inter",
		background_color: "#f7f5f0",
	});
	const [locale, setLocale] = useState("en");
	const [welcomeMessage, setWelcomeMessage] = useState("");
	const [completionMessage, setCompletionMessage] = useState(
		"Thank you for your response!",
	);

	const [createdForm, setCreatedForm] = useState<FormCreateResponse | null>(
		null,
	);
	const [status, setStatus] = useState("");
	const [saving, setSaving] = useState(false);
	const [showShare, setShowShare] = useState(false);
	const [activeTab, setActiveTab] = useState<
		"builder" | "settings" | "branding"
	>("builder");

	useEffect(() => {
		if (formId) {
			setLoadingForm(true);
			fetchForm(formId)
				.then((form) => {
					setTitle(form.title);
					setDescription(form.description);
					setSlug(form.slug);
					setMode(form.mode as "chat" | "voice" | "chat_voice");
					setPersona(form.persona);
					setSystemPrompt(form.system_prompt);
					setFields(form.fields_schema || []);
					setFormStatus(form.status);
					setLocale(form.locale || "en");
					setWelcomeMessage(form.welcome_message || "");
					setCompletionMessage(
						form.completion_message ||
							"Thank you for your response!",
					);
					if (
						form.branding &&
						Object.keys(form.branding).length > 0
					) {
						setBranding(form.branding as unknown as FormBranding);
					}
					setCreatedForm({
						id: form.id,
						org_id: form.org_id,
						slug: form.slug,
						status: form.status,
					});
				})
				.catch((err) =>
					setStatus(
						err instanceof Error
							? err.message
							: "Failed to load form",
					),
				)
				.finally(() => setLoadingForm(false));
		}
	}, [formId]);

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
			setStatus(
				"Form generated successfully! Review and save below.",
			);
		} catch (err) {
			setStatus(
				err instanceof Error ? err.message : "Failed to generate form",
			);
		} finally {
			setIsGenerating(false);
		}
	};

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
				branding,
				locale,
				welcome_message: welcomeMessage,
				completion_message: completionMessage,
			};
			const form = await createForm(orgId, payload);
			setCreatedForm(form);
			setFormStatus("draft");
			setStatus("Form created successfully!");
		} catch (err) {
			setStatus(
				err instanceof Error ? err.message : "Failed to create form",
			);
		} finally {
			setSaving(false);
		}
	};

	const handleUpdate = async () => {
		if (!createdForm) return;
		setSaving(true);
		setStatus("Saving changes...");
		try {
			await updateForm(createdForm.id, {
				title,
				description,
				slug,
				persona,
				mode,
				system_prompt: systemPrompt,
				fields,
				branding,
				locale,
				welcome_message: welcomeMessage,
				completion_message: completionMessage,
			});
			setStatus("Changes saved successfully!");
		} catch (err) {
			setStatus(
				err instanceof Error ? err.message : "Failed to save changes",
			);
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
			setFormStatus("published");
			setStatus("Form published! Consumers can now access it.");
		} catch (err) {
			setStatus(
				err instanceof Error ? err.message : "Publish failed",
			);
		} finally {
			setSaving(false);
		}
	};

	const handleUnpublish = async () => {
		if (!createdForm) return;
		setSaving(true);
		try {
			await unpublishForm(createdForm.id);
			setFormStatus("draft");
			setStatus("Form unpublished. It's now a draft.");
		} catch (err) {
			setStatus(
				err instanceof Error ? err.message : "Unpublish failed",
			);
		} finally {
			setSaving(false);
		}
	};

	const handleDuplicate = async () => {
		if (!createdForm) return;
		setSaving(true);
		try {
			const dup = await duplicateForm(createdForm.id);
			navigate(`/admin/forms/${dup.id}`);
		} catch (err) {
			setStatus(
				err instanceof Error ? err.message : "Duplicate failed",
			);
		} finally {
			setSaving(false);
		}
	};

	if (loadingForm) {
		return (
			<AdminShell
				email={admin?.email}
				onLogout={() => {
					logout();
					navigate("/admin/login");
				}}
			>
				<PageHeader title="Loading..." backTo="/admin" backLabel="Dashboard" />
				<PageBody>
					<div className="flex justify-center py-20">
						<div className="w-6 h-6 border-2 border-forest-500 border-t-transparent rounded-full animate-spin" />
					</div>
				</PageBody>
			</AdminShell>
		);
	}

	return (
		<AdminShell
			email={admin?.email}
			onLogout={() => {
				logout();
				navigate("/admin/login");
			}}
		>
			<PageHeader
				title={
					isEditMode
						? `Edit: ${title || "Form"}`
						: createdForm
							? "Form Created"
							: "Create Form"
				}
				subtitle={
					isEditMode
						? `Status: ${formStatus}`
						: "Describe what you want to collect and let AI build the form."
				}
				backTo="/admin"
				backLabel="Dashboard"
				actions={
					createdForm && (
						<div className="flex gap-2">
							<button
								type="button"
								onClick={() => setShowShare(true)}
								className="px-4 py-[7px] rounded-md text-[13px] text-text-secondary bg-bg-base border-[0.5px] border-stone-200 hover:border-stone-300"
							>
								Share
							</button>
							<button
								type="button"
								onClick={handleDuplicate}
								disabled={saving}
								className="px-4 py-[7px] rounded-md text-[13px] text-text-secondary bg-bg-base border-[0.5px] border-stone-200 hover:border-stone-300"
							>
								Duplicate
							</button>
						</div>
					)
				}
			/>
			<PageBody>
				{/* Tabs */}
				<div className="flex gap-1 mb-6 bg-stone-100 p-1 rounded-lg w-fit">
					{(
						["builder", "settings", "branding"] as const
					).map((tab) => (
						<button
							key={tab}
							type="button"
							onClick={() => setActiveTab(tab)}
							className={`px-4 py-2 rounded-md text-[13px] font-medium capitalize transition-all ${
								activeTab === tab
									? "bg-bg-base text-text-primary shadow-sm"
									: "text-text-secondary hover:text-text-primary"
							}`}
						>
							{tab}
						</button>
					))}
				</div>

				<form
					onSubmit={
						isEditMode || createdForm
							? (e) => {
									e.preventDefault();
									handleUpdate();
								}
							: handleCreate
					}
					className="space-y-6 max-w-3xl"
				>
					{activeTab === "builder" && (
						<>
							{!isEditMode && (
								<PromptFormBuilder
									prompt={prompt}
									onPromptChange={setPrompt}
									fields={fields}
									onFieldsChange={setFields}
									onGenerate={handleGenerate}
									isGenerating={isGenerating}
								/>
							)}

							{/* Fields Summary */}
							{fields.length > 0 && (
								<section className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 p-6">
									<h2 className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary mb-3">
										Fields ({fields.length})
									</h2>
									<div className="space-y-2 text-[13px]">
										{fields.map((field, i) => (
											<div
												key={field.name}
												className="flex items-center gap-3"
											>
												<span className="text-text-tertiary w-5 text-right">
													{i + 1}.
												</span>
												<span className="font-mono text-forest-600">
													{field.name}
												</span>
												<span className="text-[11px] px-2 py-0.5 rounded bg-stone-50 text-text-tertiary">
													{field.type}
												</span>
												{field.required && (
													<span className="text-[11px] text-warning">
														required
													</span>
												)}
												{field.description && (
													<span className="text-text-secondary text-[11px] truncate max-w-[200px]">
														{field.description}
													</span>
												)}
											</div>
										))}
									</div>
								</section>
							)}

							{isEditMode && (
								<PromptFormBuilder
									prompt={prompt}
									onPromptChange={setPrompt}
									fields={fields}
									onFieldsChange={setFields}
									onGenerate={handleGenerate}
									isGenerating={isGenerating}
								/>
							)}
						</>
					)}

					{activeTab === "settings" && (
						<section className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 p-6 space-y-4">
							<h2 className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary">
								Form Settings
							</h2>
							<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
								<FieldInput
									label="Title"
									id="title"
									value={title}
									onChange={setTitle}
									placeholder="Form title"
									required
								/>
								<FieldInput
									label="URL Slug"
									id="slug"
									value={slug}
									onChange={setSlug}
									placeholder="my-form"
									required
									mono
								/>
							</div>
							<div>
								<label
									htmlFor="description"
									className="block text-[13px] font-medium text-text-primary mb-[5px]"
								>
									Description
								</label>
								<textarea
									id="description"
									className="w-full px-3 py-[9px] rounded-md text-sm text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all placeholder:text-text-tertiary focus:border-forest-500 focus:shadow-forest-ring resize-none"
									value={description}
									onChange={(e) =>
										setDescription(e.target.value)
									}
									placeholder="Describe what this form collects"
									rows={2}
								/>
							</div>
							<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div>
									<label
										htmlFor="mode"
										className="block text-[13px] font-medium text-text-primary mb-[5px]"
									>
										Mode
									</label>
									<select
										id="mode"
										className="w-full px-3 py-[9px] rounded-md text-sm text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all focus:border-forest-500 focus:shadow-forest-ring"
										value={mode}
										onChange={(e) =>
											setMode(
												e.target.value as typeof mode,
											)
										}
									>
										<option value="chat">Chat only</option>
										<option value="voice">
											Voice only
										</option>
										<option value="chat_voice">
											Chat + Voice
										</option>
									</select>
								</div>
								<FieldInput
									label="Bot Persona"
									id="persona"
									value={persona}
									onChange={setPersona}
									placeholder="Friendly and professional"
								/>
							</div>
							<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div>
									<label
										htmlFor="locale"
										className="block text-[13px] font-medium text-text-primary mb-[5px]"
									>
										Language
									</label>
									<select
										id="locale"
										className="w-full px-3 py-[9px] rounded-md text-sm text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all focus:border-forest-500 focus:shadow-forest-ring"
										value={locale}
										onChange={(e) =>
											setLocale(e.target.value)
										}
									>
										<option value="en">English</option>
										<option value="es">Spanish</option>
										<option value="fr">French</option>
										<option value="de">German</option>
										<option value="pt">Portuguese</option>
										<option value="ar">Arabic</option>
										<option value="zh">Chinese</option>
										<option value="ja">Japanese</option>
										<option value="ko">Korean</option>
										<option value="hi">Hindi</option>
										<option value="ur">Urdu</option>
									</select>
								</div>
								<div />
							</div>
							<div>
								<label
									htmlFor="system-prompt"
									className="block text-[13px] font-medium text-text-primary mb-[5px]"
								>
									Agent Instructions{" "}
									<span className="text-text-tertiary font-normal">
										(auto-generated, editable)
									</span>
								</label>
								<textarea
									id="system-prompt"
									className="w-full px-3 py-[9px] rounded-md text-[13px] font-mono text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all placeholder:text-text-tertiary focus:border-forest-500 focus:shadow-forest-ring resize-none"
									value={systemPrompt}
									onChange={(e) =>
										setSystemPrompt(e.target.value)
									}
									placeholder="Instructions for the conversational agent..."
									rows={4}
								/>
							</div>
							<div>
								<label
									htmlFor="welcome-message"
									className="block text-[13px] font-medium text-text-primary mb-[5px]"
								>
									Welcome Message
								</label>
								<input
									id="welcome-message"
									className="w-full px-3 py-[9px] rounded-md text-sm text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all placeholder:text-text-tertiary focus:border-forest-500 focus:shadow-forest-ring"
									value={welcomeMessage}
									onChange={(e) =>
										setWelcomeMessage(e.target.value)
									}
									placeholder="Optional greeting before the form starts"
								/>
							</div>
							<div>
								<label
									htmlFor="completion-message"
									className="block text-[13px] font-medium text-text-primary mb-[5px]"
								>
									Completion Message
								</label>
								<input
									id="completion-message"
									className="w-full px-3 py-[9px] rounded-md text-sm text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all placeholder:text-text-tertiary focus:border-forest-500 focus:shadow-forest-ring"
									value={completionMessage}
									onChange={(e) =>
										setCompletionMessage(e.target.value)
									}
									placeholder="Thank you for your response!"
								/>
							</div>
						</section>
					)}

					{activeTab === "branding" && (
						<section className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 p-6 space-y-4">
							<h2 className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary">
								Branding & Appearance
							</h2>
							<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
								<FieldInput
									label="Logo URL"
									id="logo-url"
									value={branding.logo_url}
									onChange={(v) =>
										setBranding({ ...branding, logo_url: v })
									}
									placeholder="https://example.com/logo.png"
								/>
								<div>
									<label
										htmlFor="font"
										className="block text-[13px] font-medium text-text-primary mb-[5px]"
									>
										Font
									</label>
									<select
										id="font"
										className="w-full px-3 py-[9px] rounded-md text-sm text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all focus:border-forest-500 focus:shadow-forest-ring"
										value={branding.font}
										onChange={(e) =>
											setBranding({
												...branding,
												font: e.target.value,
											})
										}
									>
										<option value="Inter">Inter</option>
										<option value="Lora">Lora</option>
										<option value="system-ui">
											System Default
										</option>
									</select>
								</div>
							</div>
							<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
								<ColorInput
									label="Primary Color"
									value={branding.primary_color}
									onChange={(v) =>
										setBranding({
											...branding,
											primary_color: v,
										})
									}
								/>
								<ColorInput
									label="Accent Color"
									value={branding.accent_color}
									onChange={(v) =>
										setBranding({
											...branding,
											accent_color: v,
										})
									}
								/>
								<ColorInput
									label="Background"
									value={branding.background_color}
									onChange={(v) =>
										setBranding({
											...branding,
											background_color: v,
										})
									}
								/>
							</div>

							{/* Live Preview */}
							<div className="mt-6">
								<h3 className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary mb-3">
									Preview
								</h3>
								<div
									className="rounded-lg p-6 border"
									style={{
										backgroundColor:
											branding.background_color,
										fontFamily: branding.font,
									}}
								>
									{branding.logo_url && (
										<img
											src={branding.logo_url}
											alt="Logo"
											className="h-8 mb-4"
										/>
									)}
									<div
										className="text-lg font-semibold mb-2"
										style={{
											color: branding.primary_color,
										}}
									>
										{title || "Your Form Title"}
									</div>
									<div className="flex gap-2 mt-4">
										<div
											className="px-4 py-2 rounded-md text-white text-sm"
											style={{
												backgroundColor:
													branding.primary_color,
											}}
										>
											Send
										</div>
										<div
											className="px-4 py-2 rounded-md text-white text-sm"
											style={{
												backgroundColor:
													branding.accent_color,
											}}
										>
											Voice
										</div>
									</div>
								</div>
							</div>
						</section>
					)}

					{/* Actions */}
					<div className="flex flex-wrap gap-3">
						{!createdForm && !isEditMode ? (
							<button
								type="submit"
								disabled={
									saving ||
									(!systemPrompt && fields.length === 0)
								}
								className="px-6 py-[9px] rounded-md font-medium text-[13px] text-white bg-forest-500 hover:bg-forest-600 transition-all duration-150 disabled:opacity-50 shadow-forest"
							>
								{saving ? "Creating..." : "Create Draft Form"}
							</button>
						) : (
							<>
								{formStatus === "draft" && (
									<button
										type="submit"
										disabled={saving}
										className="px-6 py-[9px] rounded-md font-medium text-[13px] text-white bg-forest-500 hover:bg-forest-600 transition-all duration-150 disabled:opacity-50 shadow-forest"
									>
										{saving
											? "Saving..."
											: "Save Changes"}
									</button>
								)}
								{formStatus === "draft" ? (
									<button
										type="button"
										onClick={handlePublish}
										disabled={saving}
										className="px-6 py-[9px] rounded-md font-medium text-[13px] text-white bg-clay-500 hover:bg-clay-600 transition-all duration-150 disabled:opacity-50 shadow-clay"
									>
										{saving
											? "Publishing..."
											: "Publish Form"}
									</button>
								) : (
									<button
										type="button"
										onClick={handleUnpublish}
										disabled={saving}
										className="px-6 py-[9px] rounded-md font-medium text-[13px] text-text-secondary bg-bg-base border-[0.5px] border-stone-200 hover:border-stone-300 hover:text-text-primary transition-all"
									>
										Unpublish
									</button>
								)}
								{createdForm?.slug && (
									<Link
										to={`/f/${createdForm.slug}`}
										target="_blank"
										className="px-6 py-[9px] rounded-md text-[13px] text-text-secondary bg-bg-base border-[0.5px] border-stone-200 hover:border-stone-300 hover:text-text-primary transition-all inline-flex items-center"
									>
										Preview
									</Link>
								)}
								{createdForm && (
									<Link
										to={`/admin/forms/${createdForm.id}/submissions`}
										className="px-6 py-[9px] rounded-md text-[13px] text-text-secondary bg-bg-base border-[0.5px] border-stone-200 hover:border-stone-300 hover:text-text-primary transition-all inline-flex items-center"
									>
										Submissions
									</Link>
								)}
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
								? {
										borderColor: "var(--error-border)",
										color: "var(--color-error)",
										background: "var(--error-bg)",
									}
								: {
										borderColor: "var(--border-subtle)",
										color: "var(--text-secondary)",
										background: "var(--stone-50)",
									}
						}
					>
						{status}
					</div>
				)}

				{showShare && createdForm && (
					<ShareModal
						slug={createdForm.slug}
						onClose={() => setShowShare(false)}
					/>
				)}
			</PageBody>
		</AdminShell>
	);
}

function FieldInput({
	label,
	id,
	value,
	onChange,
	placeholder,
	required,
	mono,
}: {
	label: string;
	id: string;
	value: string;
	onChange: (v: string) => void;
	placeholder: string;
	required?: boolean;
	mono?: boolean;
}) {
	return (
		<div>
			<label
				htmlFor={id}
				className="block text-[13px] font-medium text-text-primary mb-[5px]"
			>
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

function ColorInput({
	label,
	value,
	onChange,
}: {
	label: string;
	value: string;
	onChange: (v: string) => void;
}) {
	return (
		<div>
			<label className="block text-[13px] font-medium text-text-primary mb-[5px]">
				{label}
			</label>
			<div className="flex items-center gap-2">
				<input
					type="color"
					value={value}
					onChange={(e) => onChange(e.target.value)}
					className="w-8 h-8 rounded border-[0.5px] border-stone-200 cursor-pointer"
				/>
				<input
					type="text"
					value={value}
					onChange={(e) => onChange(e.target.value)}
					className="flex-1 px-3 py-[9px] rounded-md text-[13px] font-mono text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all focus:border-forest-500 focus:shadow-forest-ring"
				/>
			</div>
		</div>
	);
}
