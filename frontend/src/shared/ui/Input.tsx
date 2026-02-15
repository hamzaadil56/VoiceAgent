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
					<label htmlFor={inputId} className="block text-sm text-text-secondary">
						{label}
					</label>
				)}
				<input
					ref={ref}
					id={inputId}
					className={`w-full px-4 py-3 glass rounded-xl border text-text-primary placeholder:text-text-tertiary focus:outline-none ${
						error ? "border-error focus:border-error" : "border-border focus:border-accent-primary"
					} ${className}`}
					aria-invalid={!!error}
					aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined}
					{...props}
				/>
				{error && (
					<p id={`${inputId}-error`} className="text-sm text-error" role="alert">
						{error}
					</p>
				)}
				{hint && !error && (
					<p id={`${inputId}-hint`} className="text-sm text-text-tertiary">
						{hint}
					</p>
				)}
			</div>
		);
	},
);

Input.displayName = "Input";

// Textarea variant
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
					<label htmlFor={inputId} className="block text-sm text-text-secondary">
						{label}
					</label>
				)}
				<textarea
					ref={ref}
					id={inputId}
					className={`w-full px-4 py-3 glass rounded-xl border text-text-primary placeholder:text-text-tertiary focus:outline-none resize-none ${
						error ? "border-error focus:border-error" : "border-border focus:border-accent-primary"
					} ${className}`}
					aria-invalid={!!error}
					{...props}
				/>
				{error && (
					<p className="text-sm text-error" role="alert">
						{error}
					</p>
				)}
			</div>
		);
	},
);

Textarea.displayName = "Textarea";
