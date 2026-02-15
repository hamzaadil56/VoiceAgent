/** Error boundary for catching render errors */
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
				<div className="min-h-screen flex items-center justify-center p-4">
					<div className="glass-elevated rounded-2xl border border-error/30 p-8 max-w-lg text-center">
						<h2 className="text-xl font-heading font-bold text-text-primary mb-2">
							Something went wrong
						</h2>
						<p className="text-text-secondary mb-4">
							An unexpected error occurred. Please try refreshing the page.
						</p>
						{this.state.error && (
							<p className="text-sm text-error/70 font-mono bg-error/5 rounded-lg p-3 mb-4">
								{this.state.error.message}
							</p>
						)}
						<button
							onClick={() => window.location.reload()}
							className="px-5 py-2.5 rounded-xl bg-accent-primary text-bg-primary font-semibold hover:opacity-90"
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
