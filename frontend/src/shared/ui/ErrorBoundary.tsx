import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
	children: ReactNode;
	fallback?: ReactNode;
}

interface State {
	hasError: boolean;
	error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
	constructor(props: Props) {
		super(props);
		this.state = { hasError: false, error: null };
	}

	static getDerivedStateFromError(error: Error): State {
		return { hasError: true, error };
	}

	componentDidCatch(error: Error, errorInfo: ErrorInfo) {
		console.error("ErrorBoundary caught:", error, errorInfo);
	}

	render() {
		if (this.state.hasError) {
			if (this.props.fallback) {
				return this.props.fallback;
			}
			return (
				<div className="min-h-screen flex items-center justify-center p-4 bg-bg-page">
					<div className="bg-bg-base rounded-xl border-[0.5px] border-stone-200 p-8 max-w-lg w-full text-center shadow-xl">
						<div className="w-12 h-12 bg-stone-50 border border-stone-200 rounded-lg grid place-items-center mx-auto mb-4 text-[24px]">
							⚠️
						</div>
						<h2 className="font-heading font-semibold text-[22px] text-text-primary mb-2">
							Something went wrong
						</h2>
						<p className="text-[13px] text-text-secondary mb-4 leading-relaxed">
							An unexpected error occurred. Please try refreshing the page.
						</p>
						{this.state.error && (
							<p className="font-mono text-[12px] rounded-md p-3 mb-4 text-left break-all text-error bg-[var(--error-bg)]">
								{this.state.error.message}
							</p>
						)}
						<button
							onClick={() => window.location.reload()}
							className="px-5 py-[9px] rounded-md bg-forest-500 text-white text-[14px] font-medium transition-all hover:bg-forest-600"
						>
							Refresh Page
						</button>
					</div>
				</div>
			);
		}

		return this.props.children;
	}
}
