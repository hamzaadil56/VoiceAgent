import { type FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { adminApi } from "../../../shared/lib/httpClient";

export default function ForgotPasswordPage() {
	const [email, setEmail] = useState("");
	const [sent, setSent] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [loading, setLoading] = useState(false);

	const onSubmit = async (event: FormEvent) => {
		event.preventDefault();
		setLoading(true);
		setError(null);
		try {
			await adminApi.post("/auth/forgot-password", { email });
			setSent(true);
		} catch (err) {
			setError(
				err instanceof Error ? err.message : "Failed to send reset link",
			);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="min-h-screen flex items-center justify-center px-8 bg-bg-page">
			<div className="w-full max-w-[400px] bg-bg-base rounded-xl border-[0.5px] border-stone-200 p-10 shadow-xl animate-fade-up">
				<div className="text-center mb-8">
					<h1 className="font-heading font-semibold text-[28px] text-text-primary leading-tight">
						Reset password
					</h1>
					<p className="text-[13px] text-text-secondary mt-2">
						Enter your email and we'll send you a reset link.
					</p>
				</div>

				{sent ? (
					<div className="text-center space-y-4">
						<div className="w-12 h-12 rounded-full bg-forest-100 grid place-items-center mx-auto">
							<svg
								className="w-6 h-6 text-forest-600"
								fill="none"
								viewBox="0 0 24 24"
								strokeWidth={1.5}
								stroke="currentColor"
							>
								<path
									strokeLinecap="round"
									strokeLinejoin="round"
									d="m4.5 12.75 6 6 9-13.5"
								/>
							</svg>
						</div>
						<p className="text-[14px] text-text-primary">
							If an account exists for that email, we've sent a reset
							link.
						</p>
						<Link
							to="/admin/login"
							className="text-[13px] text-forest-600 hover:text-forest-700 font-medium"
						>
							Back to sign in
						</Link>
					</div>
				) : (
					<form className="space-y-4" onSubmit={onSubmit}>
						<div>
							<label
								htmlFor="email"
								className="block text-[13px] font-medium text-text-primary mb-[5px]"
							>
								Email
							</label>
							<input
								id="email"
								className="w-full px-3 py-[9px] rounded-md text-text-primary text-sm border-[0.5px] border-stone-200 bg-bg-base outline-none transition-all placeholder:text-text-tertiary focus:border-forest-500 focus:shadow-forest-ring"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								placeholder="you@company.com"
								type="email"
								autoComplete="email"
								required
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
							{loading ? "Sending..." : "Send Reset Link"}
						</button>
						<p className="text-center text-[13px] text-text-secondary">
							<Link
								to="/admin/login"
								className="text-forest-600 hover:text-forest-700 font-medium"
							>
								Back to sign in
							</Link>
						</p>
					</form>
				)}
			</div>
		</div>
	);
}
