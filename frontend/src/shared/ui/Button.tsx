import { type ButtonHTMLAttributes, forwardRef } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
	variant?: ButtonVariant;
	size?: ButtonSize;
	loading?: boolean;
}

const variantStyles: Record<ButtonVariant, string> = {
	primary:
		"bg-forest-500 text-white hover:bg-forest-600 shadow-forest",
	secondary:
		"bg-transparent text-text-primary border border-stone-200 hover:border-stone-300 hover:bg-stone-50",
	ghost:
		"bg-transparent text-forest-500 hover:text-forest-600 hover:bg-forest-50",
	danger:
		"bg-clay-500 text-white hover:bg-clay-600",
};

const sizeStyles: Record<ButtonSize, string> = {
	sm: "px-3.5 py-1.5 text-xs rounded-sm",
	md: "px-5 py-[9px] text-sm rounded-md",
	lg: "px-7 py-3 text-base rounded-lg",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
	({ variant = "primary", size = "md", loading, disabled, children, className = "", ...props }, ref) => {
		return (
			<button
				ref={ref}
				disabled={disabled || loading}
				className={`font-medium inline-flex items-center justify-center gap-2 transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
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
