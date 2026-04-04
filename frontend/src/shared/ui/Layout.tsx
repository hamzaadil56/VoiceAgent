import type { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";

/* ----------------------------------------------------------------
   Admin Shell — warm stone sidebar + content
   ---------------------------------------------------------------- */

interface AdminShellProps {
	children: ReactNode;
	email?: string;
	onLogout?: () => void;
}

const navItems = [
	{ to: "/admin", label: "Dashboard", icon: DashboardIcon },
	{ to: "/admin/forms/new", label: "Create Form", icon: PlusIcon },
];

export function AdminShell({ children, email, onLogout }: AdminShellProps) {
	const location = useLocation();

	return (
		<div className="flex h-screen bg-bg-page text-text-primary">
			{/* Sidebar */}
			<aside className="w-[220px] flex-shrink-0 bg-bg-base border-r border-stone-200 flex flex-col py-4 gap-1 sticky top-0 h-screen">
				{/* Logo */}
				<div className="px-3 pb-5 flex items-center gap-2.5">
					<div className="w-7 h-7 rounded-md bg-forest-500 grid place-items-center flex-shrink-0">
						<svg width="14" height="14" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
							<path d="M12 2H4a2 2 0 0 0-2 2v12l4-4h6a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2z" />
						</svg>
					</div>
					<span className="font-heading text-[15px] font-semibold text-text-primary">
						AgentForms
					</span>
				</div>

				{/* Section label */}
				<div className="px-4 pb-2 text-[10px] text-text-tertiary font-medium uppercase tracking-[0.07em]">
					Workspace
				</div>

				{/* Nav */}
				<nav className="flex-1 flex flex-col gap-0.5 px-3">
					{navItems.map((item) => {
						const isActive = location.pathname === item.to;
						return (
							<Link
								key={item.to}
								to={item.to}
								className={`flex items-center gap-2 px-2.5 py-2 rounded-md text-[13px] transition-all duration-[120ms] ${
									isActive
										? "bg-forest-100 text-forest-600 font-medium"
										: "text-text-secondary hover:text-text-primary hover:bg-stone-50"
								}`}
							>
								<item.icon active={isActive} />
								{item.label}
							</Link>
						);
					})}
				</nav>

				{/* User / Logout */}
				<div className="px-4 pt-4 border-t border-stone-100">
					{email && (
						<p className="text-[11px] text-text-tertiary truncate mb-2 font-mono">{email}</p>
					)}
					{onLogout && (
						<button
							onClick={onLogout}
							className="w-full text-left text-[13px] text-text-secondary hover:text-text-primary py-1 transition-colors duration-[120ms]"
						>
							Sign out
						</button>
					)}
				</div>
			</aside>

			{/* Main content */}
			<main className="flex-1 overflow-y-auto flex flex-col min-w-0">
				{children}
			</main>
		</div>
	);
}

/* ----------------------------------------------------------------
   Page primitives
   ---------------------------------------------------------------- */

interface PageHeaderProps {
	title: string;
	subtitle?: string;
	backTo?: string;
	backLabel?: string;
	actions?: ReactNode;
}

export function PageHeader({ title, subtitle, backTo, backLabel, actions }: PageHeaderProps) {
	return (
		<header
			className="sticky top-0 z-20 px-8 py-5 border-b border-stone-100 flex items-center justify-between gap-4"
			style={{ background: "rgba(247,245,240,0.85)", backdropFilter: "blur(16px)", WebkitBackdropFilter: "blur(16px)" }}
		>
			<div>
				{backTo && (
					<Link
						to={backTo}
						className="text-[11px] uppercase tracking-widest font-medium text-text-tertiary hover:text-forest-500 mb-1 inline-block transition-colors"
					>
						&larr; {backLabel || "Back"}
					</Link>
				)}
				<h1 className="font-heading text-[28px] font-semibold text-text-primary leading-tight">
					{title}
				</h1>
				{subtitle && (
					<p className="text-[13px] text-text-secondary mt-0.5">{subtitle}</p>
				)}
			</div>
			{actions && <div className="flex gap-3">{actions}</div>}
		</header>
	);
}

export function PageBody({ children }: { children: ReactNode }) {
	return (
		<div className="px-8 py-6 max-w-[1200px] w-full mx-auto flex-1">
			{children}
		</div>
	);
}

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
		<div className={`${maxWidthStyles[maxWidth]} mx-auto py-8 px-4`}>
			{children}
		</div>
	);
}

export function EmptyState({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
	return (
		<div className="flex flex-col items-center justify-center py-20 px-8 text-center gap-3">
			<div className="w-12 h-12 bg-forest-100 rounded-lg grid place-items-center mb-2">
				<svg className="w-6 h-6 text-forest-500" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
					<path strokeLinecap="round" strokeLinejoin="round" d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
				</svg>
			</div>
			<h2 className="font-heading font-medium text-[18px] text-text-primary">{title}</h2>
			<p className="text-[13px] text-text-secondary max-w-[260px] leading-relaxed">{description}</p>
			{action}
		</div>
	);
}

export function ErrorDisplay({ message, retry }: { message: string; retry?: () => void }) {
	return (
		<div
			className="rounded-lg p-8 border text-center"
			style={{ background: "var(--error-bg)", borderColor: "var(--error-border)" }}
		>
			<p className="text-error mb-4 text-sm">{message}</p>
			{retry && (
				<button
					onClick={retry}
					className="px-4 py-2 rounded-md bg-bg-elevated border border-stone-200 text-text-secondary hover:text-text-primary text-[13px] transition-colors"
				>
					Try Again
				</button>
			)}
		</div>
	);
}

/* ----------------------------------------------------------------
   Icons
   ---------------------------------------------------------------- */

function DashboardIcon({ active }: { active?: boolean }) {
	return (
		<svg
			className={`w-[15px] h-[15px] flex-shrink-0 transition-colors ${active ? "text-forest-500" : "text-text-tertiary"}`}
			fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"
		>
			<rect x="3" y="3" width="7" height="7" />
			<rect x="14" y="3" width="7" height="7" />
			<rect x="14" y="14" width="7" height="7" />
			<rect x="3" y="14" width="7" height="7" />
		</svg>
	);
}

function PlusIcon({ active }: { active?: boolean }) {
	return (
		<svg
			className={`w-[15px] h-[15px] flex-shrink-0 transition-colors ${active ? "text-forest-500" : "text-text-tertiary"}`}
			fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"
		>
			<path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
		</svg>
	);
}
