import { Link } from "react-router-dom";

export default function HomePage() {
	return (
		<div className="max-w-5xl mx-auto py-10 px-4 space-y-6 relative z-10">
			<h1 className="text-5xl font-heading font-bold bg-gradient-to-r from-accent-primary via-accent-secondary to-accent-primary bg-clip-text text-transparent">
				Agentic Forms Platform
			</h1>
			<p className="text-text-secondary text-lg">
				Admins create conversational forms. Consumers answer through personalized chat or voice experiences.
			</p>
			<div className="flex flex-wrap gap-3">
				<Link
					to="/admin/login"
					className="px-5 py-3 rounded-xl bg-accent-primary text-bg-primary font-semibold hover:opacity-90"
				>
					Admin Login
				</Link>
				<Link
					to="/legacy/voice"
					className="px-5 py-3 rounded-xl glass border border-border text-text-primary hover:border-border-hover"
				>
					Legacy Voice Agent
				</Link>
			</div>
		</div>
	);
}
