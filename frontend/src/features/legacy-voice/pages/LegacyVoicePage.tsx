import { Link } from "react-router-dom";
import VoiceBot from "../../../components/VoiceBot";
import Settings from "../../../components/Settings";

export default function LegacyVoicePage() {
	return (
		<div className="min-h-screen relative z-10 bg-bg-page">
			<div className="container mx-auto px-4 py-8 relative z-10">
				<Link to="/" className="text-sm text-text-tertiary hover:text-forest-500 mb-4 inline-block transition-colors">
					&larr; Back to Home
				</Link>
				<header className="mb-12 text-center">
					<h1 className="text-5xl font-heading font-semibold mb-3 text-text-primary">
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
