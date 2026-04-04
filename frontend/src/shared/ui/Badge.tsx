type BadgeVariant = "default" | "success" | "warning" | "error" | "info" | "chat" | "voice";

interface BadgeProps {
	variant?: BadgeVariant;
	children: React.ReactNode;
	className?: string;
}

const variantStyles: Record<BadgeVariant, string> = {
	default: "bg-stone-100 text-stone-600",
	success: "bg-forest-100 text-forest-600",
	warning: "bg-[#FBF3E4] text-[#7A4F10]",
	error:   "bg-[#FBEEE8] text-[#7A2020]",
	info:    "bg-forest-100 text-forest-600",
	chat:    "bg-clay-100 text-clay-600",
	voice:   "bg-sage-100 text-sage-600",
};

export function Badge({ variant = "default", children, className = "" }: BadgeProps) {
	return (
		<span
			className={`inline-flex items-center gap-1 text-xs font-medium px-2.5 py-[3px] rounded-full ${variantStyles[variant]} ${className}`}
		>
			{children}
		</span>
	);
}

export function StatusBadge({ status }: { status: string }) {
	const variant: BadgeVariant =
		status === "published" || status === "completed" || status === "active" ? "success" :
		status === "draft" || status === "pending" || status === "paused" ? "warning" :
		status === "error" || status === "failed" || status === "closed" ? "error" :
		"default";

	return <Badge variant={variant}>{status}</Badge>;
}
