/** Hook for managing a voice session WebSocket connection (hands-free: auto-listen + VAD stop) */
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

/** VAD: avg frequency bin level (0–255) from AnalyserNode */
const VAD_SPEECH_THRESHOLD = 12;
const VAD_SILENCE_THRESHOLD = 8;
const VAD_SILENCE_DURATION_MS = 1500;

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
	/** After first server `audio_end` (greeting or first TTS turn); mic may be enabled. */
	initialAgentPlaybackDone: boolean;
	/** True while hands-free mode is active (mic auto-starts after agent; VAD ends turn). */
	isHandsFree: boolean;
	/** During listening: user has crossed speech threshold at least once this turn (for UI copy). */
	vadUserHasSpoken: boolean;
	connect: () => void;
	disconnect: () => void;
	startRecording: () => void;
	stopRecording: () => void;
}

function getSupportedMimeType(): string {
	const candidates = [
		"audio/webm;codecs=opus",
		"audio/webm",
		"audio/ogg;codecs=opus",
		"audio/mp4",
	];
	for (const mime of candidates) {
		if (MediaRecorder.isTypeSupported(mime)) return mime;
	}
	return "";
}

function streamHasLiveAudioTrack(stream: MediaStream | null): boolean {
	if (!stream) return false;
	return stream.getAudioTracks().some((t) => t.readyState === "live");
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
	const [initialAgentPlaybackDone, setInitialAgentPlaybackDone] = useState(false);
	const [vadUserHasSpoken, setVadUserHasSpoken] = useState(false);

	const wsRef = useRef<WebSocket | null>(null);
	const mediaRecorderRef = useRef<MediaRecorder | null>(null);
	const audioChunksRef = useRef<Blob[]>([]);
	/** Playback (TTS) context — 24 kHz */
	const audioContextRef = useRef<AudioContext | null>(null);
	const animFrameRef = useRef<number>(0);
	const audioQueueRef = useRef<ArrayBuffer[]>([]);
	const isPlayingRef = useRef(false);
	const stateRef = useRef<VoiceState>("disconnected");
	const pendingAudioEndRef = useRef(false);
	const onPlaybackDoneRef = useRef<(() => void) | null>(null);
	const firstServerAudioTurnDoneRef = useRef(false);
	const pendingFileReadsRef = useRef(0);
	/** Set synchronously when form completes so audio_end cannot auto-start before stateRef updates. */
	const sessionCompletedRef = useRef(false);

	/**
	 * Update stateRef synchronously so every guard that reads stateRef.current
	 * within the same event-loop turn sees the correct value.
	 * The old useEffect-based sync was deferred to after the React render,
	 * causing auto-start and VAD to see stale state and bail out.
	 */
	const setVoiceState = useCallback((next: VoiceState) => {
		stateRef.current = next;
		setState(next);
	}, []);

	/** Persistent mic capture (reused across turns) */
	const micStreamRef = useRef<MediaStream | null>(null);
	const micAnalyserCtxRef = useRef<AudioContext | null>(null);
	const micAnalyserRef = useRef<AnalyserNode | null>(null);

	const speechDetectedRef = useRef(false);
	const silenceStartRef = useRef<number | null>(null);
	const vadStoppingRef = useRef(false);
	/** If true, skip auto-start (mic denied once; user can still tap to retry). */
	const handsFreeMicBlockedRef = useRef(false);

	const startRecordingRef = useRef<() => Promise<void>>(async () => {});
	const stopRecordingRef = useRef<() => void>(() => {});

	const markFirstServerAudioTurnDone = useCallback(() => {
		if (!firstServerAudioTurnDoneRef.current) {
			firstServerAudioTurnDoneRef.current = true;
			setInitialAgentPlaybackDone(true);
		}
	}, []);

	const addMessage = useCallback(
		(msg: ChatMessage) => {
			setMessages((prev) => [...prev, msg]);
			onMessage?.(msg);
		},
		[onMessage],
	);

	const releaseMicResources = useCallback(() => {
		micStreamRef.current?.getTracks().forEach((t) => t.stop());
		micStreamRef.current = null;
		micAnalyserRef.current = null;
		void micAnalyserCtxRef.current?.close().catch(() => {});
		micAnalyserCtxRef.current = null;
		handsFreeMicBlockedRef.current = false;
	}, []);

	const ensureMicStream = useCallback(async (): Promise<boolean> => {
		if (streamHasLiveAudioTrack(micStreamRef.current) && micAnalyserRef.current) {
			return true;
		}
		releaseMicResources();
		handsFreeMicBlockedRef.current = false;
		try {
			const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
			micStreamRef.current = stream;
			const ctx = new AudioContext();
			micAnalyserCtxRef.current = ctx;
			const source = ctx.createMediaStreamSource(stream);
			const analyser = ctx.createAnalyser();
			analyser.fftSize = 256;
			source.connect(analyser);
			micAnalyserRef.current = analyser;
			return true;
		} catch {
			handsFreeMicBlockedRef.current = true;
			return false;
		}
	}, [releaseMicResources]);

	const playAudioQueue = useCallback(async () => {
		if (isPlayingRef.current) return;
		isPlayingRef.current = true;

		try {
			const ctx = audioContextRef.current || new AudioContext({ sampleRate: 24000 });
			audioContextRef.current = ctx;

			while (audioQueueRef.current.length > 0) {
				const buffer = audioQueueRef.current.shift();
				if (!buffer) continue;

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

				await new Promise<void>((resolve) => {
					source.onended = () => resolve();
				});
			}
		} catch (err) {
			console.warn("Audio playback error:", err);
		} finally {
			isPlayingRef.current = false;
			if (pendingAudioEndRef.current && audioQueueRef.current.length === 0) {
				pendingAudioEndRef.current = false;
				onPlaybackDoneRef.current?.();
			}
		}
	}, []);

	const tryAutoStartListening = useCallback(() => {
		if (sessionCompletedRef.current || stateRef.current === "completed") return;
		if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
		if (handsFreeMicBlockedRef.current) return;
		if (isPlayingRef.current) return;
		queueMicrotask(() => {
			void startRecordingRef.current();
		});
	}, []);

	const connect = useCallback(() => {
		if (wsRef.current?.readyState === WebSocket.OPEN) return;

		setVoiceState("connecting");
		setError(null);
		firstServerAudioTurnDoneRef.current = false;
		sessionCompletedRef.current = false;
		setInitialAgentPlaybackDone(false);

		const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
		const wsUrl = `${protocol}//${window.location.host}/v1/public/sessions/${sessionId}/voice`;

		const ws = new WebSocket(wsUrl);
		wsRef.current = ws;

		ws.onopen = () => {
			ws.send(JSON.stringify({ type: "auth", token: sessionToken }));
		};

		ws.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data);

				switch (data.type) {
					case "state":
						if (data.data === "connected") {
							setError(null);
							setVoiceState("connected");
						}
						break;

					case "assistant_message":
						addMessage({
							role: "assistant",
							content: data.data,
							timestamp: Date.now(),
						});
						if (data.state === "completed") {
							sessionCompletedRef.current = true;
							setVoiceState("completed");
						} else {
							setVoiceState("speaking");
						}
						break;

					case "transcription":
						addMessage({
							role: "user",
							content: data.data,
							timestamp: Date.now(),
						});
						setVoiceState("processing");
						break;

					case "audio_chunk":
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

					case "audio_end": {
						pendingAudioEndRef.current = true;
						onPlaybackDoneRef.current = () => {
							markFirstServerAudioTurnDone();
							if (!sessionCompletedRef.current && stateRef.current !== "completed") {
								setVoiceState("connected");
								tryAutoStartListening();
							}
							onPlaybackDoneRef.current = null;
						};
						if (!isPlayingRef.current && audioQueueRef.current.length === 0) {
							pendingAudioEndRef.current = false;
							markFirstServerAudioTurnDone();
							if (!sessionCompletedRef.current && stateRef.current !== "completed") {
								setVoiceState("connected");
								tryAutoStartListening();
							}
							onPlaybackDoneRef.current = null;
						}
						break;
					}

					case "error":
						setError(data.data);
						setVoiceState("error");
						break;
				}
			} catch {
				// ignore parse errors
			}
		};

		ws.onclose = () => {
			setVoiceState("disconnected");
		};

		ws.onerror = () => {
			if (stateRef.current === "connecting") {
				setVoiceState("error");
				setError("WebSocket connection failed");
			}
		};
	}, [sessionId, sessionToken, addMessage, playAudioQueue, markFirstServerAudioTurnDone, tryAutoStartListening, setVoiceState]);

	const stopRecording = useCallback(() => {
		const recorder = mediaRecorderRef.current;
		if (!recorder || recorder.state === "inactive") {
			wsRef.current?.send(JSON.stringify({ type: "stop" }));
			mediaRecorderRef.current = null;
			return;
		}

		if (vadStoppingRef.current) return;
		vadStoppingRef.current = true;

		cancelAnimationFrame(animFrameRef.current);
		setAudioLevel(0);
		setVadUserHasSpoken(false);
		speechDetectedRef.current = false;
		silenceStartRef.current = null;

		if (stateRef.current === "listening") {
			setVoiceState("processing");
		}

		const sendStopWhenReady = () => {
			const deadline = Date.now() + 3000;
			const tick = () => {
				if (pendingFileReadsRef.current <= 0 || Date.now() > deadline) {
					wsRef.current?.send(JSON.stringify({ type: "stop" }));
					mediaRecorderRef.current = null;
					vadStoppingRef.current = false;
					return;
				}
				setTimeout(tick, 15);
			};
			setTimeout(tick, 0);
		};

		recorder.onstop = () => {
			// Do NOT stop mic tracks — stream is persistent for hands-free turns
			sendStopWhenReady();
		};
		recorder.stop();
	}, [setVoiceState]);

	const startRecording = useCallback(async () => {
		if (!firstServerAudioTurnDoneRef.current) return;
		const st = stateRef.current;
		if (st !== "connected" && st !== "error") return;
		if (isPlayingRef.current) return;
		if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") return;

		if (st === "error") {
			setError(null);
			setVoiceState("connected");
		}

		const ok = await ensureMicStream();
		if (!ok || !micStreamRef.current || !micAnalyserRef.current) {
			setError("Microphone access denied");
			setVoiceState("error");
			return;
		}

		const mimeType = getSupportedMimeType();
		const options: MediaRecorderOptions = mimeType ? { mimeType } : {};
		let mediaRecorder: MediaRecorder;
		try {
			mediaRecorder = new MediaRecorder(micStreamRef.current, options);
		} catch {
			setError("Recording not supported in this browser");
			setVoiceState("error");
			return;
		}

		mediaRecorderRef.current = mediaRecorder;
		audioChunksRef.current = [];
		pendingFileReadsRef.current = 0;
		speechDetectedRef.current = false;
		silenceStartRef.current = null;
		setVadUserHasSpoken(false);
		vadStoppingRef.current = false;

		const analyser = micAnalyserRef.current;
		const dataArray = new Uint8Array(analyser.frequencyBinCount);

		const updateLevel = () => {
			if (stateRef.current !== "listening" || !mediaRecorderRef.current || mediaRecorderRef.current.state !== "recording") {
				return;
			}

			analyser.getByteFrequencyData(dataArray);
			const average = dataArray.reduce((sum, v) => sum + v, 0) / dataArray.length;
			setAudioLevel(Math.min(average / 128, 1));

			if (average >= VAD_SPEECH_THRESHOLD) {
				speechDetectedRef.current = true;
				silenceStartRef.current = null;
				setVadUserHasSpoken(true);
			} else if (average < VAD_SILENCE_THRESHOLD && speechDetectedRef.current) {
				if (silenceStartRef.current === null) {
					silenceStartRef.current = Date.now();
				} else if (Date.now() - silenceStartRef.current >= VAD_SILENCE_DURATION_MS) {
					stopRecordingRef.current();
					return;
				}
			}

			animFrameRef.current = requestAnimationFrame(updateLevel);
		};

		mediaRecorder.ondataavailable = (e) => {
			if (e.data.size > 0) {
				audioChunksRef.current.push(e.data);

				pendingFileReadsRef.current += 1;
				const reader = new FileReader();
				reader.onloadend = () => {
					pendingFileReadsRef.current -= 1;
					try {
						const base64 = (reader.result as string).split(",")[1];
						if (base64) {
							wsRef.current?.send(JSON.stringify({ type: "audio_chunk", data: base64 }));
						}
					} catch {
						// ignore
					}
				};
				reader.onerror = () => {
					pendingFileReadsRef.current -= 1;
				};
				reader.readAsDataURL(e.data);
			}
		};

		mediaRecorder.start(250);
		wsRef.current?.send(JSON.stringify({ type: "start_recording" }));
		setVoiceState("listening");
		animFrameRef.current = requestAnimationFrame(updateLevel);
	}, [ensureMicStream, setVoiceState]);

	useEffect(() => {
		startRecordingRef.current = startRecording;
	}, [startRecording]);

	useEffect(() => {
		stopRecordingRef.current = stopRecording;
	}, [stopRecording]);

	const disconnect = useCallback(() => {
		if (wsRef.current) {
			wsRef.current.close();
			wsRef.current = null;
		}
		if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
			mediaRecorderRef.current.stop();
		}
		mediaRecorderRef.current = null;
		cancelAnimationFrame(animFrameRef.current);
		releaseMicResources();
		setVadUserHasSpoken(false);
		setVoiceState("disconnected");
	}, [releaseMicResources, setVoiceState]);

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
		initialAgentPlaybackDone,
		isHandsFree: true,
		vadUserHasSpoken,
		connect,
		disconnect,
		startRecording,
		stopRecording,
	};
}
