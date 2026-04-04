import { type InputHTMLAttributes, forwardRef } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
	label?: string;
	error?: string;
	hint?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
	({ label, error, hint, id, className = "", ...props }, ref) => {
		const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");

		return (
			<div className="space-y-1">
				{label && (
					<label htmlFor={inputId} className="block text-[13px] font-medium text-text-primary">
						{label}
					</label>
				)}
				<input
					ref={ref}
					id={inputId}
					className={`w-full px-3 py-[9px] bg-bg-base rounded-md border-[0.5px] text-text-primary text-sm placeholder:text-text-tertiary focus:outline-none focus:border-forest-500 focus:shadow-forest-ring transition-all ${
						error ? "border-error shadow-[0_0_0_3px_rgba(140,32,32,0.1)]" : "border-stone-200"
					} ${className}`}
					aria-invalid={!!error}
					aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined}
					{...props}
				/>
				{error && (
					<p id={`${inputId}-error`} className="text-xs text-error" role="alert">
						{error}
					</p>
				)}
				{hint && !error && (
					<p id={`${inputId}-hint`} className="text-xs text-text-tertiary">
						{hint}
					</p>
				)}
			</div>
		);
	},
);

Input.displayName = "Input";

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
	label?: string;
	error?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
	({ label, error, id, className = "", ...props }, ref) => {
		const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");

		return (
			<div className="space-y-1">
				{label && (
					<label htmlFor={inputId} className="block text-[13px] font-medium text-text-primary">
						{label}
					</label>
				)}
				<textarea
					ref={ref}
					id={inputId}
					className={`w-full px-3 py-[9px] bg-bg-base rounded-md border-[0.5px] text-text-primary text-sm placeholder:text-text-tertiary focus:outline-none focus:border-forest-500 focus:shadow-forest-ring resize-none transition-all ${
						error ? "border-error shadow-[0_0_0_3px_rgba(140,32,32,0.1)]" : "border-stone-200"
					} ${className}`}
					aria-invalid={!!error}
					{...props}
				/>
				{error && (
					<p className="text-xs text-error" role="alert">
						{error}
					</p>
				)}
			</div>
		);
	},
);

Textarea.displayName = "Textarea";
