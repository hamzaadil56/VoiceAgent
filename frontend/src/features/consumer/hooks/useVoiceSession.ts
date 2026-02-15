/** Hook for managing a voice session WebSocket connection */
import { useCallback, useEffect, useRef, useState } from "react";
import type { ChatMessage } from "../../../shared/types/api";

export type VoiceState =
	| "disconnected"
	| "connecting"
	| "connected"
	| "listening"
	| "processing"
	| "speaking"
	| "completed"
	| "error";

interface UseVoiceSessionOptions {
	sessionId: string;
	sessionToken: string;
	onMessage?: (msg: ChatMessage) => void;
}

interface UseVoiceSessionReturn {
	state: VoiceState;
	messages: ChatMessage[];
	error: string | null;
	audioLevel: number;
	connect: () => void;
	disconnect: () => void;
	startRecording: () => void;
	stopRecording: () => void;
}

export function useVoiceSession({
	sessionId,
	sessionToken,
	onMessage,
}: UseVoiceSessionOptions): UseVoiceSessionReturn {
	const [state, setState] = useState<VoiceState>("disconnected");
	const [messages, setMessages] = useState<ChatMessage[]>([]);
	const [error, setError] = useState<string | null>(null);
	const [audioLevel, setAudioLevel] = useState(0);

	const wsRef = useRef<WebSocket | null>(null);
	const mediaRecorderRef = useRef<MediaRecorder | null>(null);
	const audioChunksRef = useRef<Blob[]>([]);
	const audioContextRef = useRef<AudioContext | null>(null);
	const analyserRef = useRef<AnalyserNode | null>(null);
	const animFrameRef = useRef<number>(0);
	const audioQueueRef = useRef<ArrayBuffer[]>([]);
	const isPlayingRef = useRef(false);

	const addMessage = useCallback(
		(msg: ChatMessage) => {
			setMessages((prev) => [...prev, msg]);
			onMessage?.(msg);
		},
		[onMessage],
	);

	const connect = useCallback(() => {
		if (wsRef.current?.readyState === WebSocket.OPEN) return;

		setState("connecting");
		setError(null);

		const wsBase = (
			import.meta.env.VITE_WS_URL ||
			import.meta.env.VITE_BACKEND_URL ||
			"http://localhost:8000"
		).replace(/^http/, "ws");

		const ws = new WebSocket(`${wsBase}/v1/public/sessions/${sessionId}/voice`);
		wsRef.current = ws;

		ws.onopen = () => {
			// Send auth message
			ws.send(JSON.stringify({ type: "auth", token: sessionToken }));
		};

		ws.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data);

				switch (data.type) {
					case "state":
						if (data.data === "connected") {
							setState("connected");
						}
						break;

					case "assistant_message":
						addMessage({
							role: "assistant",
							content: data.data,
							timestamp: Date.now(),
						});
						if (data.state === "completed") {
							setState("completed");
						} else {
							setState("speaking");
						}
						break;

					case "transcription":
						addMessage({
							role: "user",
							content: data.data,
							timestamp: Date.now(),
						});
						setState("processing");
						break;

					case "audio_chunk":
						// Decode and queue PCM audio for playback
						if (data.data) {
							try {
								const binaryString = atob(data.data);
								const bytes = new Uint8Array(binaryString.length);
								for (let i = 0; i < binaryString.length; i++) {
									bytes[i] = binaryString.charCodeAt(i);
								}
								audioQueueRef.current.push(bytes.buffer);
								if (!isPlayingRef.current) {
									playAudioQueue();
								}
							} catch {
								// ignore decode errors
							}
						}
						break;

					case "audio_end":
						// Audio finished, go back to connected
						setTimeout(() => {
							if (state !== "completed") {
								setState("connected");
							}
						}, 500);
						break;

					case "error":
						setError(data.data);
						setState("error");
						break;
				}
			} catch {
				// ignore parse errors
			}
		};

		ws.onclose = () => {
			setState("disconnected");
		};

		ws.onerror = () => {
			setState("error");
			setError("WebSocket connection failed");
		};
	}, [sessionId, sessionToken, addMessage, state]);

	const playAudioQueue = useCallback(async () => {
		if (isPlayingRef.current) return;
		isPlayingRef.current = true;

		try {
			const ctx = audioContextRef.current || new AudioContext({ sampleRate: 24000 });
			audioContextRef.current = ctx;

			while (audioQueueRef.current.length > 0) {
				const buffer = audioQueueRef.current.shift();
				if (!buffer) continue;

				// Convert Int16 PCM to Float32 for Web Audio
				const int16Array = new Int16Array(buffer);
				const float32Array = new Float32Array(int16Array.length);
				for (let i = 0; i < int16Array.length; i++) {
					float32Array[i] = int16Array[i] / 32768;
				}

				const audioBuffer = ctx.createBuffer(1, float32Array.length, 24000);
				audioBuffer.getChannelData(0).set(float32Array);

				const source = ctx.createBufferSource();
				source.buffer = audioBuffer;
				source.connect(ctx.destination);
				source.start();

				// Wait for playback to finish
				await new Promise<void>((resolve) => {
					source.onended = () => resolve();
				});
			}
		} catch (err) {
			console.warn("Audio playback error:", err);
		} finally {
			isPlayingRef.current = false;
		}
	}, []);

	const disconnect = useCallback(() => {
		if (wsRef.current) {
			wsRef.current.close();
			wsRef.current = null;
		}
		if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
			mediaRecorderRef.current.stop();
		}
		cancelAnimationFrame(animFrameRef.current);
		setState("disconnected");
	}, []);

	const startRecording = useCallback(async () => {
		try {
			const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
			const mediaRecorder = new MediaRecorder(stream, {
				mimeType: "audio/webm;codecs=opus",
			});
			mediaRecorderRef.current = mediaRecorder;
			audioChunksRef.current = [];

			// Set up audio level monitoring
			const ctx = new AudioContext();
			const source = ctx.createMediaStreamSource(stream);
			const analyser = ctx.createAnalyser();
			analyser.fftSize = 256;
			source.connect(analyser);
			analyserRef.current = analyser;

			const dataArray = new Uint8Array(analyser.frequencyBinCount);
			const updateLevel = () => {
				analyser.getByteFrequencyData(dataArray);
				const average = dataArray.reduce((sum, v) => sum + v, 0) / dataArray.length;
				setAudioLevel(Math.min(average / 128, 1));
				animFrameRef.current = requestAnimationFrame(updateLevel);
			};
			updateLevel();

			mediaRecorder.ondataavailable = (e) => {
				if (e.data.size > 0) {
					audioChunksRef.current.push(e.data);

					// Stream chunks to server as base64
					const reader = new FileReader();
					reader.onloadend = () => {
						const base64 = (reader.result as string).split(",")[1];
						wsRef.current?.send(
							JSON.stringify({ type: "audio_chunk", data: base64 }),
						);
					};
					reader.readAsDataURL(e.data);
				}
			};

			mediaRecorder.start(250); // Send chunks every 250ms
			setState("listening");
		} catch (err) {
			setError("Microphone access denied");
			setState("error");
		}
	}, []);

	const stopRecording = useCallback(() => {
		cancelAnimationFrame(animFrameRef.current);
		setAudioLevel(0);

		if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
			mediaRecorderRef.current.stop();
			mediaRecorderRef.current.stream.getTracks().forEach((t) => t.stop());
		}

		setState("processing");

		// Send stop signal to server
		wsRef.current?.send(JSON.stringify({ type: "stop" }));
	}, []);

	// Cleanup on unmount
	useEffect(() => {
		return () => {
			disconnect();
		};
	}, [disconnect]);

	return {
		state,
		messages,
		error,
		audioLevel,
		connect,
		disconnect,
		startRecording,
		stopRecording,
	};
}
