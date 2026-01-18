import { useState } from "react";
import VoiceBot from "./components/VoiceBot";
import Settings from "./components/Settings";

type View = "voicebot" | "settings";

function App() {
	const [view, setView] = useState<View>("voicebot");

	return (
		<div className="min-h-screen bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-700">
			<div className="container mx-auto px-4 py-8">
				<header className="mb-8 text-center">
					<h1 className="text-4xl font-bold text-white mb-2">
						🎙️ Voice Agent
					</h1>
					<p className="text-white/80">AI-powered voice assistant</p>
				</header>

				<div className="flex justify-center mb-4">
					<div className="bg-white/10 backdrop-blur-sm rounded-lg p-1 inline-flex">
						<button
							onClick={() => setView("voicebot")}
							className={`px-6 py-2 rounded-md transition-all ${
								view === "voicebot"
									? "bg-white text-purple-600 font-semibold"
									: "text-white hover:bg-white/10"
							}`}
						>
							Voice Bot
						</button>
						<button
							onClick={() => setView("settings")}
							className={`px-6 py-2 rounded-md transition-all ${
								view === "settings"
									? "bg-white text-purple-600 font-semibold"
									: "text-white hover:bg-white/10"
							}`}
						>
							Settings
						</button>
					</div>
				</div>

				<main className="max-w-4xl mx-auto">
					{view === "voicebot" ? <VoiceBot /> : <Settings />}
				</main>
			</div>
		</div>
	);
}

export default App;
