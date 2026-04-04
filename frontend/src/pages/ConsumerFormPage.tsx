import { FormEvent, useMemo, useState } from "react";
import { createPublicSession, sendPublicMessage } from "../lib/agenticApi";

type ChatItem = { role: "assistant" | "user"; text: string };

export default function ConsumerFormPage() {
	const slug = useMemo(() => {
		const parts = window.location.pathname.split("/").filter(Boolean);
		return parts.length >= 2 ? parts[1] : "";
	}, []);
	const [sessionId, setSessionId] = useState("");
	const [sessionToken, setSessionToken] = useState("");
	const [chat, setChat] = useState<ChatItem[]>([]);
	const [input, setInput] = useState("");
	const [status, setStatus] = useState("Ready");
	const [channel, setChannel] = useState<"chat" | "voice">("chat");

	const isStarted = useMemo(() => Boolean(sessionId && sessionToken), [sessionId, sessionToken]);

	const startSession = async () => {
		if (!slug) return;
		setStatus("Starting session...");
		try {
			const response = await createPublicSession(slug, channel);
			setSessionId(response.session_id);
			setSessionToken(response.session_token);
			setChat([{ role: "assistant", text: response.assistant_message }]);
			setStatus("Session started");
		} catch (err) {
			setStatus(err instanceof Error ? err.message : "Failed to start session");
		}
	};

	const send = async (event: FormEvent) => {
		event.preventDefault();
		if (!input.trim() || !sessionId || !sessionToken) return;

		const message = input.trim();
		setInput("");
		setChat((items) => [...items, { role: "user", text: message }]);

		try {
			const response = await sendPublicMessage(sessionId, sessionToken, message);
			setChat((items) => [...items, { role: "assistant", text: response.assistant_message }]);
			setStatus(response.state === "completed" ? "Completed" : "Collecting responses");
		} catch (err) {
			setStatus(err instanceof Error ? err.message : "Failed to send message");
		}
	};

	return (
		<div className="max-w-3xl mx-auto px-4 py-8">
			<h1 className="text-3xl font-heading text-text-primary mb-2">Agentic Form</h1>
			<p className="text-text-secondary mb-6">Form slug: <code>{slug}</code></p>

			{!isStarted ? (
				<div className="glass-elevated rounded-2xl border border-border/40 p-6 space-y-4">
					<label className="text-sm text-text-secondary">Interaction Mode</label>
					<select value={channel} onChange={(e) => setChannel(e.target.value as "chat" | "voice")} className="w-full px-4 py-3 rounded-xl glass border border-border">
						<option value="chat">Chat</option>
						<option value="voice">Voice</option>
					</select>
					<button onClick={startSession} className="px-5 py-3 rounded-xl bg-accent-primary text-bg-primary font-semibold">Start Form</button>
					{channel === "voice" && <p className="text-xs text-text-tertiary">Voice mode currently uses text fallback submission in this build.</p>}
				</div>
			) : (
				<div className="glass-elevated rounded-2xl border border-border/40 p-6">
					<div className="max-h-[420px] overflow-y-auto space-y-3 mb-4">
						{chat.map((item, index) => (
							<div key={index} className={`p-3 rounded-xl ${item.role === "assistant" ? "bg-accent-secondary/10" : "bg-accent-primary/10"}`}>
								<p className="text-xs uppercase tracking-wide opacity-70 mb-1">{item.role}</p>
								<p>{item.text}</p>
							</div>
						))}
					</div>
					<form className="flex gap-2" onSubmit={send}>
						<input value={input} onChange={(e) => setInput(e.target.value)} className="flex-1 px-4 py-3 rounded-xl glass border border-border" placeholder="Type your answer" />
						<button className="px-4 py-3 rounded-xl bg-accent-primary text-bg-primary" type="submit">Send</button>
					</form>
				</div>
			)}

			<p className="mt-4 text-text-secondary text-sm">Status: {status}</p>
		</div>
	);
}
