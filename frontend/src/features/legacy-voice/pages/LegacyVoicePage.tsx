import { Link } from "react-router-dom";
import VoiceBot from "../../../components/VoiceBot";
import Settings from "../../../components/Settings";

export default function LegacyVoicePage() {
	return (
		<div className="min-h-screen relative z-10">
			<div className="container mx-auto px-4 py-8 relative z-10">
				<Link to="/" className="text-sm text-text-tertiary hover:text-accent-primary mb-4 inline-block">
					&larr; Back to Home
				</Link>
				<header className="mb-12 text-center">
					<h1 className="text-6xl font-heading font-bold mb-3 bg-gradient-to-r from-accent-primary via-accent-secondary to-accent-primary bg-clip-text text-transparent">
						Voice Agent (Legacy)
					</h1>
				</header>
				<div className="max-w-5xl mx-auto space-y-8">
					<VoiceBot />
					<Settings />
				</div>
			</div>
		</div>
	);
}
