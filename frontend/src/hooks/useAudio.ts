import { useEffect, useRef, useState } from "react";
import { AudioRecorder } from "../utils/audioRecorder";
import { AudioPlayer } from "../utils/audioPlayer";

export function useAudio() {
	const recorderRef = useRef<AudioRecorder | null>(null);
	const playerRef = useRef<AudioPlayer | null>(null);
	const [isRecording, setIsRecording] = useState(false);
	const [isPlaying, setIsPlaying] = useState(false);
	const [isInitialized, setIsInitialized] = useState(false);

	useEffect(() => {
		// Initialize audio components
		// Create instances immediately (synchronously) so they exist even if initialization is async
		recorderRef.current = new AudioRecorder();
		playerRef.current = new AudioPlayer();

		const init = async () => {
			try {
				await recorderRef.current!.initialize();
				await playerRef.current!.initialize();

				setIsInitialized(true);
			} catch (error) {
				console.error("Failed to initialize audio:", error);
				// Reset refs on failure
				recorderRef.current = null;
				playerRef.current = null;
			}
		};

		init();

		return () => {
			// Cleanup
			if (recorderRef.current) {
				recorderRef.current.cleanup();
			}
			if (playerRef.current) {
				playerRef.current.cleanup();
			}
		};
	}, []);

	const startRecording = async (onChunk?: (base64: string) => void) => {
		if (!recorderRef.current || !isInitialized) {
			throw new Error("Audio not initialized");
		}

		const onChunkWrapper = async (blob: Blob) => {
			if (onChunk) {
				const base64 = await recorderRef.current!.blobToBase64(blob);
				onChunk(base64);
			}
		};

		recorderRef.current.startRecording(onChunkWrapper);
		setIsRecording(true);
	};

	const stopRecording = async (): Promise<string> => {
		if (!recorderRef.current) {
			throw new Error("Recorder not initialized");
		}

		const blob = await recorderRef.current.stopRecording();
		setIsRecording(false);
		return await recorderRef.current.blobToBase64(blob);
	};

	const playAudio = async (base64Audio: string) => {
		if (!playerRef.current || !isInitialized) {
			throw new Error("Audio player not initialized");
		}

		setIsPlaying(true);
		try {
			await playerRef.current.playChunk(base64Audio);
		} finally {
			setIsPlaying(false);
		}
	};

	const playPCMAudio = async (base64PCM: string) => {
		// Ensure player instance exists (create if initialization hasn't completed yet)
		if (!playerRef.current) {
			console.log(
				"⚠️ AudioPlayer not initialized yet, creating instance..."
			);
			playerRef.current = new AudioPlayer();
		}

		// playPCMChunk will handle audioContext initialization if needed
		setIsPlaying(true);
		try {
			await playerRef.current.playPCMChunk(base64PCM);
		} catch (error) {
			console.error("Error in playPCMChunk:", error);
			throw error;
		} finally {
			setIsPlaying(false);
		}
	};

	const playPCMChunks = async (base64Chunks: string[]) => {
		// Ensure player instance exists
		if (!playerRef.current) {
			console.log(
				"⚠️ AudioPlayer not initialized yet, creating instance..."
			);
			playerRef.current = new AudioPlayer();
		}

		setIsPlaying(true);
		try {
			await playerRef.current.playPCMChunks(base64Chunks);
		} catch (error) {
			console.error("Error in playPCMChunks:", error);
			throw error;
		} finally {
			setIsPlaying(false);
		}
	};

	return {
		isInitialized,
		isRecording,
		isPlaying,
		startRecording,
		stopRecording,
		playAudio,
		playPCMAudio,
		playPCMChunks, // New method for buffered chunks
	};
}
