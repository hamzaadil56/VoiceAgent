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
		<div className="min-h-screen flex items-center justify-center px-8 bg-bg-page">
			<div className="w-full max-w-[400px] bg-bg-base rounded-xl border-[0.5px] border-stone-200 p-10 shadow-xl animate-fade-up">
				{/* Logo */}
				<div className="text-center mb-8">
					<div className="w-12 h-12 rounded-lg bg-forest-500 grid place-items-center mx-auto mb-4 text-white shadow-forest">
						<svg width="24" height="24" fill="none" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
							<path d="M20 2H8a4 4 0 0 0-4 4v20l8-8h8a4 4 0 0 0 4-4V6a4 4 0 0 0-4-4z" />
						</svg>
					</div>
					<h1 className="font-heading font-semibold text-[28px] text-text-primary leading-tight">
						Welcome back
					</h1>
					<p className="text-[13px] text-text-secondary mt-2">
						Sign in to manage your agentic forms.
					</p>
				</div>

				<form className="space-y-4" onSubmit={onSubmit}>
					<div>
						<label htmlFor="email" className="block text-[13px] font-medium text-text-primary mb-[5px]">
							Email
						</label>
						<input
							id="email"
							className="w-full px-3 py-[9px] rounded-md text-text-primary text-sm border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all placeholder:text-text-tertiary focus:border-forest-500 focus:shadow-forest-ring"
							value={email}
							onChange={(e) => setEmail(e.target.value)}
							placeholder="admin@example.com"
							type="email"
							autoComplete="email"
						/>
					</div>
					<div>
						<label htmlFor="password" className="block text-[13px] font-medium text-text-primary mb-[5px]">
							Password
						</label>
						<input
							id="password"
							className="w-full px-3 py-[9px] rounded-md text-text-primary text-sm border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all placeholder:text-text-tertiary focus:border-forest-500 focus:shadow-forest-ring"
							type="password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							placeholder="Password"
							autoComplete="current-password"
						/>
					</div>
					{error && (
						<p className="text-[13px] text-error" role="alert">
							{error}
						</p>
					)}
					<button
						className="w-full px-6 py-[9px] rounded-md font-medium text-[14px] text-white bg-forest-500 hover:bg-forest-600 transition-all duration-150 disabled:opacity-50 shadow-forest"
						disabled={loading}
						type="submit"
					>
						{loading ? "Signing in..." : "Sign In"}
					</button>
				</form>
			</div>
		</div>
	);
}
