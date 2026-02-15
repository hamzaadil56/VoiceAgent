import { FormEvent, useState } from "react";
import { loginAdmin, setAdminToken } from "../lib/agenticApi";

export default function AdminLoginPage() {
	const [email, setEmail] = useState("admin@example.com");
	const [password, setPassword] = useState("admin123");
	const [error, setError] = useState<string | null>(null);
	const [loading, setLoading] = useState(false);

	const onSubmit = async (event: FormEvent) => {
		event.preventDefault();
		setLoading(true);
		setError(null);
		try {
			const data = await loginAdmin(email, password);
			setAdminToken(data.access_token);
			window.location.href = "/admin";
		} catch (err) {
			setError(err instanceof Error ? err.message : "Login failed");
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="max-w-lg mx-auto mt-20 glass-elevated rounded-3xl p-8 border border-border/40">
			<h1 className="text-3xl font-heading font-bold text-text-primary mb-2">Admin Login</h1>
			<p className="text-text-secondary mb-6">Sign in to create and manage agentic forms.</p>
			<form className="space-y-4" onSubmit={onSubmit}>
				<input className="w-full px-4 py-3 glass rounded-xl border border-border text-text-primary" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
				<input className="w-full px-4 py-3 glass rounded-xl border border-border text-text-primary" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" />
				{error && <p className="text-error text-sm">{error}</p>}
				<button className="w-full px-6 py-3 rounded-xl bg-accent-primary text-bg-primary font-semibold" disabled={loading} type="submit">
					{loading ? "Signing in..." : "Sign in"}
				</button>
			</form>
		</div>
	);
}
