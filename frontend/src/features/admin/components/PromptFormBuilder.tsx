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
	"text", "email", "number", "phone", "url", "date", "select", "boolean",
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
			{ name: `field_${Date.now()}`, type: "text", required: true, description: "" },
		]);
	}, [onFieldsChange]);

	const removeField = useCallback(
		(index: number) => { onFieldsChange((prev) => prev.filter((_, i) => i !== index)); },
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
			{/* AI Prompt */}
			<section className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 p-6 space-y-4">
				<div>
					<h2 className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary mb-1">
						Describe Your Form
					</h2>
					<p className="text-[13px] text-text-secondary">
						Tell the AI what information you want to collect. Be specific about field types and validation.
					</p>
				</div>

				<textarea
					value={prompt}
					onChange={(e) => onPromptChange(e.target.value)}
					className="w-full px-3 py-[9px] rounded-md text-sm text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all placeholder:text-text-tertiary focus:border-forest-500 focus:shadow-forest-ring resize-none"
					placeholder="Example: I want to collect leads for my real estate business. I need their full name, email address, phone number, budget range, preferred neighborhood, and when they're looking to buy."
					rows={5}
				/>

				<button
					type="button"
					onClick={onGenerate}
					disabled={isGenerating || prompt.trim().length < 10}
					className="px-6 py-[9px] rounded-md font-medium text-[13px] text-white bg-forest-500 hover:bg-forest-600 transition-all duration-150 disabled:opacity-50 shadow-forest flex items-center gap-2"
				>
					{isGenerating ? (
						<>
							<span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
							Generating...
						</>
					) : (
						<>
							<svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
								<path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 0 0-2.455 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" />
							</svg>
							Generate with AI
						</>
					)}
				</button>
			</section>

			{/* Fields */}
			<section className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 p-6 space-y-4">
				<div className="flex items-center justify-between">
					<div>
						<h2 className="text-[11px] font-medium uppercase tracking-[0.06em] text-text-tertiary mb-1">
							Form Fields
						</h2>
						<p className="text-[13px] text-text-secondary">
							{fields.length} field{fields.length !== 1 ? "s" : ""} — edit or add more
						</p>
					</div>
					<button
						type="button"
						onClick={addField}
						className="px-3 py-[6px] text-[13px] rounded-md font-medium text-forest-600 border-[0.5px] border-forest-200 bg-forest-50 hover:bg-forest-100 transition-all"
					>
						+ Add Field
					</button>
				</div>

				{fields.length === 0 ? (
					<div className="text-center py-8">
						<p className="text-text-tertiary text-[13px]">
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

interface FieldCardProps {
	field: FormField;
	index: number;
	totalFields: number;
	onUpdate: (updates: Partial<FormField>) => void;
	onRemove: () => void;
}

function FieldCard({ field, index, totalFields, onUpdate, onRemove }: FieldCardProps) {
	return (
		<div className="bg-stone-50 rounded-md border-[0.5px] border-stone-100 p-4 space-y-3 group">
			<div className="flex items-center justify-between">
				<div className="flex items-center gap-2">
					<span className="font-mono text-[11px] px-2 py-0.5 rounded bg-stone-100 text-text-tertiary">
						#{index + 1}
					</span>
					<span className="font-mono text-[11px] text-text-tertiary">{field.name}</span>
				</div>
				{totalFields > 1 && (
					<button
						type="button"
						onClick={onRemove}
						className="px-1.5 py-0.5 text-[11px] text-error opacity-0 group-hover:opacity-100 transition-opacity"
					>
						Remove
					</button>
				)}
			</div>

			<div className="grid grid-cols-1 md:grid-cols-4 gap-3">
				<input
					className="px-3 py-2 rounded-md font-mono text-[13px] text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all focus:border-forest-500 focus:shadow-forest-ring"
					value={field.name}
					onChange={(e) => onUpdate({ name: e.target.value.replace(/\s+/g, "_").toLowerCase() })}
					placeholder="field_name"
				/>
				<input
					className="md:col-span-3 px-3 py-2 rounded-md text-[13px] text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all focus:border-forest-500 focus:shadow-forest-ring"
					value={field.description}
					onChange={(e) => onUpdate({ description: e.target.value })}
					placeholder="Field description..."
				/>
			</div>

			<div className="flex flex-wrap gap-3 items-center">
				<select
					className="px-3 py-2 rounded-md text-[13px] text-text-primary border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all focus:border-forest-500 focus:shadow-forest-ring"
					value={field.type}
					onChange={(e) => onUpdate({ type: e.target.value as FormField["type"] })}
				>
					{FIELD_TYPES.map((t) => (
						<option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
					))}
				</select>

				<label className="flex items-center gap-2 text-[13px] text-text-secondary cursor-pointer">
					<input
						type="checkbox"
						checked={field.required}
						onChange={(e) => onUpdate({ required: e.target.checked })}
						className="rounded accent-forest-500"
					/>
					Required
				</label>
			</div>
		</div>
	);
}
