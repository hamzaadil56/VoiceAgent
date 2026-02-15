import type { ReactNode } from "react";
import { Link } from "react-router-dom";

interface PageLayoutProps {
	children: ReactNode;
	maxWidth?: "sm" | "md" | "lg" | "xl" | "2xl";
}

const maxWidthStyles = {
	sm: "max-w-lg",
	md: "max-w-2xl",
	lg: "max-w-4xl",
	xl: "max-w-6xl",
	"2xl": "max-w-7xl",
};

export function PageLayout({ children, maxWidth = "xl" }: PageLayoutProps) {
	return (
		<div className={`${maxWidthStyles[maxWidth]} mx-auto py-8 px-4 relative z-10`}>
			{children}
		</div>
	);
}

interface PageHeaderProps {
	title: string;
	subtitle?: string;
	backTo?: string;
	backLabel?: string;
	actions?: ReactNode;
}

export function PageHeader({ title, subtitle, backTo, backLabel, actions }: PageHeaderProps) {
	return (
		<div className="mb-6">
			{backTo && (
				<Link
					to={backTo}
					className="text-sm text-text-tertiary hover:text-accent-primary mb-2 inline-block"
				>
					&larr; {backLabel || "Back"}
				</Link>
			)}
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-2xl font-heading font-bold text-text-primary">
						{title}
					</h1>
					{subtitle && (
						<p className="text-sm text-text-secondary mt-1">{subtitle}</p>
					)}
				</div>
				{actions && <div className="flex gap-3">{actions}</div>}
			</div>
		</div>
	);
}

/** Empty state component */
interface EmptyStateProps {
	title: string;
	description: string;
	action?: ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
	return (
		<div className="glass-elevated rounded-2xl p-12 border border-border/40 text-center">
			<h2 className="text-xl font-heading text-text-primary mb-2">{title}</h2>
			<p className="text-text-secondary mb-6">{description}</p>
			{action}
		</div>
	);
}

/** Error display */
export function ErrorDisplay({ message, retry }: { message: string; retry?: () => void }) {
	return (
		<div className="glass-elevated rounded-2xl p-8 border border-error/30 text-center">
			<p className="text-error mb-4">{message}</p>
			{retry && (
				<button
					onClick={retry}
					className="px-4 py-2 rounded-lg glass border border-border text-text-secondary hover:text-text-primary"
				>
					Try Again
				</button>
			)}
		</div>
	);
}
