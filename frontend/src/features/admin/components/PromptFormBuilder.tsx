/** Prompt-based form builder — admin writes requirements, AI generates form fields */
import { type Dispatch, type SetStateAction, useCallback } from "react";
import type { FormField } from "../../../shared/types/api";

interface PromptFormBuilderProps {
	prompt: string;
	onPromptChange: (prompt: string) => void;
	fields: FormField[];
	onFieldsChange: Dispatch<SetStateAction<FormField[]>>;
	onGenerate: () => Promise<void>;
	isGenerating: boolean;
}

const FIELD_TYPES = [
	"text",
	"email",
	"number",
	"phone",
	"url",
	"date",
	"select",
	"boolean",
] as const;

export function PromptFormBuilder({
	prompt,
	onPromptChange,
	fields,
	onFieldsChange,
	onGenerate,
	isGenerating,
}: PromptFormBuilderProps) {
	const addField = useCallback(() => {
		onFieldsChange((prev) => [
			...prev,
			{
				name: `field_${Date.now()}`,
				type: "text",
				required: true,
				description: "",
			},
		]);
	}, [onFieldsChange]);

	const removeField = useCallback(
		(index: number) => {
			onFieldsChange((prev) => prev.filter((_, i) => i !== index));
		},
		[onFieldsChange],
	);

	const updateField = useCallback(
		(index: number, updates: Partial<FormField>) => {
			onFieldsChange((prev) => {
				const updated = [...prev];
				updated[index] = { ...updated[index], ...updates };
				return updated;
			});
		},
		[onFieldsChange],
	);

	return (
		<div className="space-y-6">
			{/* AI Prompt Section */}
			<section className="glass-elevated rounded-2xl p-6 border border-border/40 space-y-4">
				<div>
					<h2 className="text-lg font-heading text-text-primary">
						Describe Your Form
					</h2>
					<p className="text-sm text-text-tertiary mt-1">
						Tell the AI what information you want to collect. Be as specific as
						you like — include field types, validation rules, and conversation
						style.
					</p>
				</div>

				<textarea
					value={prompt}
					onChange={(e) => onPromptChange(e.target.value)}
					className="w-full px-4 py-3 glass rounded-xl border border-border text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-accent-primary resize-none"
					placeholder="Example: I want to collect leads for my real estate business. I need their full name, email address, phone number, budget range (a number between $50k and $5M), preferred neighborhood, and when they're looking to buy. Be friendly and professional."
					rows={5}
				/>

				<button
					type="button"
					onClick={onGenerate}
					disabled={isGenerating || prompt.trim().length < 10}
					className="px-6 py-3 rounded-xl bg-accent-primary text-bg-primary font-semibold hover:opacity-90 disabled:opacity-50 flex items-center gap-2"
				>
					{isGenerating ? (
						<>
							<span className="w-4 h-4 border-2 border-bg-primary border-t-transparent rounded-full animate-spin" />
							Generating...
						</>
					) : (
						<>
							<svg
								className="w-5 h-5"
								fill="none"
								viewBox="0 0 24 24"
								strokeWidth={1.5}
								stroke="currentColor"
							>
								<path
									strokeLinecap="round"
									strokeLinejoin="round"
									d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 0 0-2.455 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z"
								/>
							</svg>
							Generate Form with AI
						</>
					)}
				</button>
			</section>

			{/* Generated Fields Section */}
			<section className="glass-elevated rounded-2xl p-6 border border-border/40 space-y-4">
				<div className="flex items-center justify-between">
					<div>
						<h2 className="text-lg font-heading text-text-primary">
							Form Fields
						</h2>
						<p className="text-sm text-text-tertiary">
							{fields.length} field{fields.length !== 1 ? "s" : ""} — edit or
							add more below
						</p>
					</div>
					<button
						type="button"
						onClick={addField}
						className="px-4 py-2 text-sm rounded-xl bg-accent-primary/10 text-accent-primary hover:bg-accent-primary/20 font-medium"
					>
						+ Add Field
					</button>
				</div>

				{fields.length === 0 ? (
					<div className="text-center py-8">
						<p className="text-text-tertiary mb-3">
							No fields yet. Use AI generation above or add fields manually.
						</p>
					</div>
				) : (
					<div className="space-y-3">
						{fields.map((field, index) => (
							<FieldCard
								key={`${field.name}-${index}`}
								field={field}
								index={index}
								totalFields={fields.length}
								onUpdate={(updates) => updateField(index, updates)}
								onRemove={() => removeField(index)}
							/>
						))}
					</div>
				)}
			</section>
		</div>
	);
}

// --- Field Card ---

interface FieldCardProps {
	field: FormField;
	index: number;
	totalFields: number;
	onUpdate: (updates: Partial<FormField>) => void;
	onRemove: () => void;
}

function FieldCard({
	field,
	index,
	totalFields,
	onUpdate,
	onRemove,
}: FieldCardProps) {
	return (
		<div className="glass rounded-xl p-4 border border-border/30 space-y-3 group">
			<div className="flex items-center justify-between">
				<div className="flex items-center gap-2">
					<span className="text-xs text-text-tertiary font-mono bg-surface/50 px-2 py-0.5 rounded">
						#{index + 1}
					</span>
					<span className="text-xs text-text-tertiary font-mono">
						{field.name}
					</span>
				</div>
				{totalFields > 1 && (
					<button
						type="button"
						onClick={onRemove}
						className="px-1.5 py-0.5 text-xs text-error/70 hover:text-error opacity-0 group-hover:opacity-100 transition-opacity"
					>
						Remove
					</button>
				)}
			</div>

			<div className="grid grid-cols-1 md:grid-cols-4 gap-3">
				<input
					className="px-3 py-2 glass rounded-lg border border-border text-sm text-text-primary focus:outline-none focus:border-accent-primary"
					value={field.name}
					onChange={(e) =>
						onUpdate({
							name: e.target.value.replace(/\s+/g, "_").toLowerCase(),
						})
					}
					placeholder="field_name"
				/>
				<input
					className="md:col-span-3 px-3 py-2 glass rounded-lg border border-border text-sm text-text-primary focus:outline-none focus:border-accent-primary"
					value={field.description}
					onChange={(e) => onUpdate({ description: e.target.value })}
					placeholder="Field description..."
				/>
			</div>

			<div className="flex flex-wrap gap-3 items-center">
				<select
					className="px-3 py-2 glass rounded-lg border border-border text-sm text-text-primary focus:outline-none focus:border-accent-primary"
					value={field.type}
					onChange={(e) =>
						onUpdate({ type: e.target.value as FormField["type"] })
					}
				>
					{FIELD_TYPES.map((t) => (
						<option key={t} value={t}>
							{t.charAt(0).toUpperCase() + t.slice(1)}
						</option>
					))}
				</select>

				<label className="flex items-center gap-2 text-sm text-text-secondary cursor-pointer">
					<input
						type="checkbox"
						checked={field.required}
						onChange={(e) => onUpdate({ required: e.target.checked })}
						className="rounded accent-accent-primary"
					/>
					Required
				</label>
			</div>
		</div>
	);
}
