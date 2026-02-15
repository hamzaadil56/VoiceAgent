import type { HTMLAttributes, ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
	elevated?: boolean;
	children: ReactNode;
}

export function Card({ elevated = false, children, className = "", ...props }: CardProps) {
	return (
		<div
			className={`rounded-2xl border border-border/40 p-6 ${
				elevated ? "glass-elevated" : "glass"
			} ${className}`}
			{...props}
		>
			{children}
		</div>
	);
}

interface CardHeaderProps {
	title: string;
	description?: string;
	action?: ReactNode;
}

export function CardHeader({ title, description, action }: CardHeaderProps) {
	return (
		<div className="flex items-center justify-between mb-4">
			<div>
				<h2 className="text-lg font-heading font-bold text-text-primary">
					{title}
				</h2>
				{description && (
					<p className="text-sm text-text-secondary mt-0.5">{description}</p>
				)}
			</div>
			{action && <div>{action}</div>}
		</div>
	);
}
