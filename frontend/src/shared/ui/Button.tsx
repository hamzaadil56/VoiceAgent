import { type ButtonHTMLAttributes, forwardRef } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
	variant?: ButtonVariant;
	size?: ButtonSize;
	loading?: boolean;
}

const variantStyles: Record<ButtonVariant, string> = {
	primary: "bg-accent-primary text-bg-primary hover:opacity-90",
	secondary: "glass border border-border text-text-primary hover:border-border-hover",
	ghost: "text-text-secondary hover:text-text-primary hover:bg-surface/50",
	danger: "bg-error/20 text-error hover:bg-error/30 border border-error/30",
};

const sizeStyles: Record<ButtonSize, string> = {
	sm: "px-3 py-1.5 text-sm rounded-lg",
	md: "px-5 py-2.5 rounded-xl",
	lg: "px-6 py-3 rounded-xl text-base",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
	({ variant = "primary", size = "md", loading, disabled, children, className = "", ...props }, ref) => {
		return (
			<button
				ref={ref}
				disabled={disabled || loading}
				className={`font-semibold inline-flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
				{...props}
			>
				{loading && (
					<span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
				)}
				{children}
			</button>
		);
	},
);

Button.displayName = "Button";
