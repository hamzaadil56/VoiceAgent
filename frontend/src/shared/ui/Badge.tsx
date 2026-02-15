type BadgeVariant = "default" | "success" | "warning" | "error" | "info";

interface BadgeProps {
	variant?: BadgeVariant;
	children: React.ReactNode;
	className?: string;
}

const variantStyles: Record<BadgeVariant, string> = {
	default: "bg-text-tertiary/20 text-text-secondary",
	success: "bg-success/20 text-success",
	warning: "bg-warning/20 text-warning",
	error: "bg-error/20 text-error",
	info: "bg-info/20 text-info",
};

export function Badge({ variant = "default", children, className = "" }: BadgeProps) {
	return (
		<span
			className={`inline-flex items-center text-xs font-medium px-2.5 py-0.5 rounded-full ${variantStyles[variant]} ${className}`}
		>
			{children}
		</span>
	);
}

/** Convenience wrappers for common status badges */
export function StatusBadge({ status }: { status: string }) {
	const variant: BadgeVariant =
		status === "published" || status === "completed" ? "success" :
		status === "draft" || status === "pending" ? "warning" :
		status === "error" || status === "failed" ? "error" :
		status === "active" ? "info" : "default";

	return <Badge variant={variant}>{status}</Badge>;
}
