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
			const response = await fetch(
				`${import.meta.env.VITE_BACKEND_URL}/api/settings`
			);
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
			const response = await fetch(
				`${import.meta.env.VITE_BACKEND_URL}/api/settings`,
				{
					method: "PUT",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify(updates),
				}
			);

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
			<div className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 shadow-md p-10 text-center">
				<div className="flex flex-col items-center gap-4">
					<div className="w-12 h-12 border-4 border-forest-500 border-t-transparent rounded-full animate-spin"></div>
					<p className="text-text-secondary">
						Loading settings...
					</p>
				</div>
			</div>
		);
	}

	if (!settings) {
		return (
			<div className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 shadow-md p-10 text-center">
				<p className="text-error mb-6">
					Failed to load settings
				</p>
				<button
					onClick={fetchSettings}
					className="px-6 py-[9px] bg-forest-500 text-white rounded-md hover:bg-forest-600 font-medium transition-all shadow-forest"
				>
					Retry
				</button>
			</div>
		);
	}

	const inputClass = "w-full px-4 py-[9px] bg-bg-base text-text-primary rounded-md border-[0.5px] border-stone-200 focus:outline-none focus:border-forest-500 focus:shadow-forest-ring transition-all text-sm";

	return (
		<div className="bg-bg-base rounded-lg border-[0.5px] border-stone-200 shadow-md p-10">
			<h2 className="text-2xl font-heading font-semibold text-text-primary mb-8">
				Settings
			</h2>

			{message && (
				<div
					className={`mb-6 p-4 rounded-md border-[0.5px] text-sm ${
						message.type === "success"
							? "bg-forest-50 border-forest-200 text-forest-600"
							: "text-error"
					}`}
					style={message.type === "error" ? { background: "var(--error-bg)", borderColor: "var(--error-border)" } : undefined}
				>
					{message.text}
				</div>
			)}

			<form onSubmit={handleSave} className="space-y-6">
				<div className="space-y-1">
					<label className="block text-[13px] font-medium text-text-primary">
						Agent Name
					</label>
					<input
						type="text"
						name="agent_name"
						defaultValue={settings.agent_name}
						className={inputClass}
						placeholder="Enter agent name"
					/>
				</div>

				<div className="space-y-1">
					<label className="block text-[13px] font-medium text-text-primary">
						TTS Voice
					</label>
					<select
						name="tts_voice"
						defaultValue={settings.tts_voice}
						className={`${inputClass} appearance-none cursor-pointer`}
					>
						{AVAILABLE_VOICES.map((voice) => (
							<option key={voice} value={voice}>
								{voice.charAt(0).toUpperCase() + voice.slice(1)}
							</option>
						))}
					</select>
				</div>

				<div className="space-y-2">
					<div className="flex justify-between items-center">
						<label className="block text-[13px] font-medium text-text-primary">
							Temperature
						</label>
						<span className="text-forest-500 font-medium text-lg">
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
						className="w-full h-2 bg-stone-100 rounded-lg appearance-none cursor-pointer accent-forest-500"
					/>
					<p className="text-text-tertiary text-xs mt-1">
						Controls randomness (0.0 = deterministic, 1.0 = creative)
					</p>
				</div>

				<div className="space-y-1">
					<label className="block text-[13px] font-medium text-text-primary">
						Max Tokens
					</label>
					<input
						type="number"
						name="max_tokens"
						min="100"
						max="2000"
						step="100"
						defaultValue={settings.max_tokens}
						className={inputClass}
						placeholder="Enter max tokens"
					/>
				</div>

				<div className="space-y-1">
					<label className="block text-[13px] font-medium text-text-primary">
						Max Turns
					</label>
					<input
						type="number"
						name="max_turns"
						min="1"
						max="5"
						step="1"
						defaultValue={settings.max_turns}
						className={inputClass}
						placeholder="Enter max turns"
					/>
					<p className="text-text-tertiary text-xs mt-1">
						Maximum number of conversation turns (1-5)
					</p>
				</div>

				<div className="bg-stone-50 rounded-md p-5 border-[0.5px] border-stone-100">
					<h3 className="text-text-primary font-heading font-medium mb-4 text-base">
						Model Information
					</h3>
					<div className="space-y-2 text-sm">
						<div className="flex justify-between items-center py-2 border-b border-stone-100">
							<span className="text-text-tertiary text-xs uppercase tracking-wider">
								STT Model
							</span>
							<span className="text-text-primary font-medium">
								{settings.stt_model}
							</span>
						</div>
						<div className="flex justify-between items-center py-2">
							<span className="text-text-tertiary text-xs uppercase tracking-wider">
								LLM Model
							</span>
							<span className="text-text-primary font-medium">
								{settings.llm_model}
							</span>
						</div>
					</div>
				</div>

				<button
					type="submit"
					disabled={saving}
					className="w-full px-6 py-3 bg-forest-500 hover:bg-forest-600 disabled:bg-stone-200 disabled:text-stone-400 disabled:cursor-not-allowed text-white rounded-md font-medium transition-all shadow-forest disabled:shadow-none"
				>
					{saving ? (
						<span className="flex items-center justify-center gap-2">
							<div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
							Saving...
						</span>
					) : (
						"Save Settings"
					)}
				</button>
			</form>
		</div>
	);
}
