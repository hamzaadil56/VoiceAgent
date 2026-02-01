import { useState, useEffect } from "react";

interface SettingsData {
	agent_name: string;
	tts_voice: string;
	temperature: number;
	max_tokens: number;
	stt_model: string;
	llm_model: string;
	max_turns: number;
}

const AVAILABLE_VOICES = [
	"tara",
	"leah",
	"jess",
	"leo",
	"dan",
	"mia",
	"zac",
	"zoe",
];

export default function Settings() {
	const [settings, setSettings] = useState<SettingsData | null>(null);
	const [loading, setLoading] = useState(true);
	const [saving, setSaving] = useState(false);
	const [message, setMessage] = useState<{
		type: "success" | "error";
		text: string;
	} | null>(null);

	useEffect(() => {
		fetchSettings();
	}, []);

	const fetchSettings = async () => {
		try {
			const response = await fetch("http://localhost:8000/api/settings");
			if (response.ok) {
				const data = await response.json();
				setSettings(data);
			} else {
				setMessage({ type: "error", text: "Failed to load settings" });
			}
		} catch (error) {
			console.error("Error fetching settings:", error);
			setMessage({ type: "error", text: "Failed to connect to server" });
		} finally {
			setLoading(false);
		}
	};

	const handleSave = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		setSaving(true);
		setMessage(null);

		const formData = new FormData(e.currentTarget);
		const updates: Partial<SettingsData> = {};

		if (formData.get("agent_name")) {
			updates.agent_name = formData.get("agent_name") as string;
		}
		if (formData.get("tts_voice")) {
			updates.tts_voice = formData.get("tts_voice") as string;
		}
		if (formData.get("temperature")) {
			updates.temperature = parseFloat(
				formData.get("temperature") as string
			);
		}
		if (formData.get("max_tokens")) {
			updates.max_tokens = parseInt(formData.get("max_tokens") as string);
		}
		if (formData.get("max_turns")) {
			updates.max_turns = parseInt(formData.get("max_turns") as string);
		}

		try {
			const response = await fetch("http://localhost:8000/api/settings", {
				method: "PUT",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(updates),
			});

			if (response.ok) {
				const data = await response.json();
				setSettings(data.settings);
				setMessage({
					type: "success",
					text: "Settings updated successfully!",
				});
			} else {
				setMessage({
					type: "error",
					text: "Failed to update settings",
				});
			}
		} catch (error) {
			console.error("Error updating settings:", error);
			setMessage({ type: "error", text: "Failed to connect to server" });
		} finally {
			setSaving(false);
		}
	};

	if (loading) {
		return (
			<div className="glass-elevated rounded-3xl shadow-2xl p-10 text-center border border-border/50">
				<div className="flex flex-col items-center gap-4">
					<div className="w-12 h-12 border-4 border-accent-primary border-t-transparent rounded-full animate-spin-slow"></div>
					<p className="text-text-secondary font-body">Loading settings...</p>
				</div>
			</div>
		);
	}

	if (!settings) {
		return (
			<div className="glass-elevated rounded-3xl shadow-2xl p-10 text-center border border-border/50">
				<p className="text-error font-body mb-6">Failed to load settings</p>
				<button
					onClick={fetchSettings}
					className="px-6 py-3 bg-accent-primary text-bg-primary rounded-lg hover:bg-accent-secondary font-body font-semibold transition-all shadow-lg shadow-accent-primary/50 hover:shadow-accent-secondary/50"
				>
					Retry
				</button>
			</div>
		);
	}

	return (
		<div className="glass-elevated rounded-3xl shadow-2xl p-10 border border-border/50">
			<h2 className="text-3xl font-heading font-bold text-text-primary mb-8 tracking-tight">Settings</h2>

			{message && (
				<div
					className={`mb-6 p-4 rounded-xl border ${
						message.type === "success"
							? "bg-success/10 border-success/30 text-success"
							: "bg-error/10 border-error/30 text-error"
					} font-body`}
				>
					{message.text}
				</div>
			)}

			<form onSubmit={handleSave} className="space-y-8">
				<div className="space-y-2">
					<label className="block text-text-primary font-heading font-semibold text-sm uppercase tracking-wider mb-3">
						Agent Name
					</label>
					<input
						type="text"
						name="agent_name"
						defaultValue={settings.agent_name}
						className="w-full px-5 py-3 glass text-text-primary rounded-xl border border-border focus:outline-none focus:ring-2 focus:ring-accent-primary/50 focus:border-accent-primary transition-all font-body"
						placeholder="Enter agent name"
					/>
				</div>

				<div className="space-y-2">
					<label className="block text-text-primary font-heading font-semibold text-sm uppercase tracking-wider mb-3">
						TTS Voice
					</label>
					<select
						name="tts_voice"
						defaultValue={settings.tts_voice}
						className="w-full px-5 py-3 glass text-text-primary rounded-xl border border-border focus:outline-none focus:ring-2 focus:ring-accent-primary/50 focus:border-accent-primary transition-all font-body appearance-none cursor-pointer"
					>
						{AVAILABLE_VOICES.map((voice) => (
							<option
								key={voice}
								value={voice}
								className="bg-bg-tertiary text-text-primary"
							>
								{voice.charAt(0).toUpperCase() + voice.slice(1)}
							</option>
						))}
					</select>
				</div>

				<div className="space-y-3">
					<div className="flex justify-between items-center">
						<label className="block text-text-primary font-heading font-semibold text-sm uppercase tracking-wider">
							Temperature
						</label>
						<span className="text-accent-primary font-body font-semibold text-lg">
							{settings.temperature}
						</span>
					</div>
					<input
						type="range"
						name="temperature"
						min="0"
						max="1"
						step="0.1"
						defaultValue={settings.temperature}
						className="w-full h-2 bg-surface rounded-lg appearance-none cursor-pointer accent-accent-primary"
						style={{
							background: `linear-gradient(to right, var(--color-accent-primary) 0%, var(--color-accent-primary) ${(settings.temperature * 100)}%, var(--color-surface) ${(settings.temperature * 100)}%, var(--color-surface) 100%)`
						}}
					/>
					<p className="text-text-tertiary text-xs font-body mt-2">
						Controls randomness (0.0 = deterministic, 1.0 = creative)
					</p>
				</div>

				<div className="space-y-2">
					<label className="block text-text-primary font-heading font-semibold text-sm uppercase tracking-wider mb-3">
						Max Tokens
					</label>
					<input
						type="number"
						name="max_tokens"
						min="100"
						max="2000"
						step="100"
						defaultValue={settings.max_tokens}
						className="w-full px-5 py-3 glass text-text-primary rounded-xl border border-border focus:outline-none focus:ring-2 focus:ring-accent-primary/50 focus:border-accent-primary transition-all font-body"
						placeholder="Enter max tokens"
					/>
				</div>

				<div className="space-y-2">
					<label className="block text-text-primary font-heading font-semibold text-sm uppercase tracking-wider mb-3">
						Max Turns
					</label>
					<input
						type="number"
						name="max_turns"
						min="1"
						max="5"
						step="1"
						defaultValue={settings.max_turns}
						className="w-full px-5 py-3 glass text-text-primary rounded-xl border border-border focus:outline-none focus:ring-2 focus:ring-accent-primary/50 focus:border-accent-primary transition-all font-body"
						placeholder="Enter max turns"
					/>
					<p className="text-text-tertiary text-xs font-body mt-2">
						Maximum number of conversation turns (1-5)
					</p>
				</div>

				<div className="glass rounded-xl p-6 border border-border/30">
					<h3 className="text-text-primary font-heading font-semibold mb-4 text-lg tracking-tight">
						Model Information
					</h3>
					<div className="space-y-2 font-body text-sm">
						<div className="flex justify-between items-center py-2 border-b border-border/20">
							<span className="text-text-tertiary uppercase text-xs tracking-wider">STT Model</span>
							<span className="text-text-primary font-medium">{settings.stt_model}</span>
						</div>
						<div className="flex justify-between items-center py-2">
							<span className="text-text-tertiary uppercase text-xs tracking-wider">LLM Model</span>
							<span className="text-text-primary font-medium">{settings.llm_model}</span>
						</div>
					</div>
				</div>

				<button
					type="submit"
					disabled={saving}
					className="w-full px-6 py-4 bg-accent-primary hover:bg-accent-secondary disabled:bg-surface disabled:cursor-not-allowed text-bg-primary rounded-xl font-heading font-semibold transition-all shadow-lg shadow-accent-primary/50 hover:shadow-accent-secondary/50 disabled:shadow-none relative overflow-hidden group"
				>
					{saving ? (
						<span className="flex items-center justify-center gap-2">
							<div className="w-4 h-4 border-2 border-bg-primary border-t-transparent rounded-full animate-spin"></div>
							Saving...
						</span>
					) : (
						<>
							<span className="relative z-10">Save Settings</span>
							<span className="absolute inset-0 bg-gradient-to-r from-accent-primary to-accent-secondary opacity-0 group-hover:opacity-100 transition-opacity"></span>
						</>
					)}
				</button>
			</form>
		</div>
	);
}
