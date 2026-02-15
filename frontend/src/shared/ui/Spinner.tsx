interface SpinnerProps {
	size?: "sm" | "md" | "lg";
	className?: string;
}

const sizeStyles = {
	sm: "w-4 h-4 border-2",
	md: "w-8 h-8 border-2",
	lg: "w-12 h-12 border-3",
};

export function Spinner({ size = "md", className = "" }: SpinnerProps) {
	return (
		<div
			className={`border-accent-primary border-t-transparent rounded-full animate-spin ${sizeStyles[size]} ${className}`}
			role="status"
			aria-label="Loading"
		>
			<span className="sr-only">Loading...</span>
		</div>
	);
}

/** Full-page centered spinner */
export function PageLoader() {
	return (
		<div className="flex items-center justify-center min-h-screen">
			<Spinner size="lg" />
		</div>
	);
}

/** Inline loading indicator */
export function InlineLoader({ text = "Loading..." }: { text?: string }) {
	return (
		<div className="flex items-center gap-3 py-8 justify-center">
			<Spinner size="sm" />
			<span className="text-text-secondary text-sm">{text}</span>
		</div>
	);
}
