import { type FormEvent, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../../../app/AuthProvider";

export default function LoginPage() {
	const { login, isAuthenticated } = useAuth();
	const navigate = useNavigate();
	const [searchParams] = useSearchParams();
	const redirectTo = searchParams.get("redirect") || "/admin";

	const [email, setEmail] = useState("admin@example.com");
	const [password, setPassword] = useState("admin123");
	const [error, setError] = useState<string | null>(null);
	const [loading, setLoading] = useState(false);

	// Already logged in - redirect
	if (isAuthenticated) {
		navigate(redirectTo, { replace: true });
		return null;
	}

	const onSubmit = async (event: FormEvent) => {
		event.preventDefault();
		setLoading(true);
		setError(null);
		try {
			await login(email, password);
			navigate(redirectTo, { replace: true });
		} catch (err) {
			setError(err instanceof Error ? err.message : "Login failed");
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="min-h-screen flex items-center justify-center relative z-10 px-4">
			<div className="w-full max-w-lg glass-elevated rounded-3xl p-8 border border-border/40">
				<h1 className="text-3xl font-heading font-bold text-text-primary mb-2">
					Admin Login
				</h1>
				<p className="text-text-secondary mb-6">
					Sign in to create and manage agentic forms.
				</p>
				<form className="space-y-4" onSubmit={onSubmit}>
					<div>
						<label htmlFor="email" className="block text-sm text-text-secondary mb-1">
							Email
						</label>
						<input
							id="email"
							className="w-full px-4 py-3 glass rounded-xl border border-border text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-accent-primary"
							value={email}
							onChange={(e) => setEmail(e.target.value)}
							placeholder="admin@example.com"
							type="email"
							autoComplete="email"
						/>
					</div>
					<div>
						<label htmlFor="password" className="block text-sm text-text-secondary mb-1">
							Password
						</label>
						<input
							id="password"
							className="w-full px-4 py-3 glass rounded-xl border border-border text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-accent-primary"
							type="password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							placeholder="Password"
							autoComplete="current-password"
						/>
					</div>
					{error && (
						<p className="text-error text-sm" role="alert">
							{error}
						</p>
					)}
					<button
						className="w-full px-6 py-3 rounded-xl bg-accent-primary text-bg-primary font-semibold hover:opacity-90 disabled:opacity-50"
						disabled={loading}
						type="submit"
					>
						{loading ? "Signing in..." : "Sign in"}
					</button>
				</form>
			</div>
		</div>
	);
}
