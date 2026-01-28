import { useState } from "react";
import VoiceBot from "./components/VoiceBot";
import Settings from "./components/Settings";

type View = "voicebot" | "settings";

function App() {
	const [view, setView] = useState<View>("voicebot");

	return (
		<div className="min-h-screen relative z-10">
			<div className="container mx-auto px-4 py-8 relative z-10">
				<header className="mb-12 text-center animate-fade-in">
					<h1 className="text-6xl font-heading font-bold mb-3 bg-gradient-to-r from-accent-primary via-accent-secondary to-accent-primary bg-clip-text text-transparent animate-glow">
						Voice Agent
					</h1>
					<p className="text-text-secondary text-lg font-body font-light tracking-wide">
						AI-powered voice assistant
					</p>
					<div className="mt-4 flex justify-center items-center gap-2">
						<div className="w-2 h-2 rounded-full bg-accent-primary animate-pulse"></div>
						<span className="text-text-tertiary text-sm font-body">Active</span>
					</div>
				</header>

				<div className="flex justify-center mb-8 animate-slide-up" style={{ animationDelay: '0.2s' }}>
					<div className="glass rounded-xl p-1 inline-flex gap-1">
						<button
							onClick={() => setView("voicebot")}
							className={`px-8 py-3 rounded-lg transition-all duration-300 font-body font-medium relative overflow-hidden ${
								view === "voicebot"
									? "bg-accent-primary text-bg-primary font-semibold shadow-lg shadow-accent-primary/50"
									: "text-text-secondary hover:text-text-primary hover:bg-surface"
							}`}
						>
							{view === "voicebot" && (
								<span className="absolute inset-0 bg-gradient-to-r from-accent-primary to-accent-secondary opacity-20 animate-shimmer" 
									style={{ backgroundSize: '200% 100%' }}></span>
							)}
							<span className="relative z-10">Voice Bot</span>
						</button>
						<button
							onClick={() => setView("settings")}
							className={`px-8 py-3 rounded-lg transition-all duration-300 font-body font-medium relative overflow-hidden ${
								view === "settings"
									? "bg-accent-primary text-bg-primary font-semibold shadow-lg shadow-accent-primary/50"
									: "text-text-secondary hover:text-text-primary hover:bg-surface"
							}`}
						>
							{view === "settings" && (
								<span className="absolute inset-0 bg-gradient-to-r from-accent-primary to-accent-secondary opacity-20 animate-shimmer" 
									style={{ backgroundSize: '200% 100%' }}></span>
							)}
							<span className="relative z-10">Settings</span>
						</button>
					</div>
				</div>

				<main className="max-w-5xl mx-auto animate-scale-in" style={{ animationDelay: '0.3s' }}>
					{view === "voicebot" ? <VoiceBot /> : <Settings />}
				</main>
			</div>
		</div>
	);
}

export default App;
