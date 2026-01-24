import { useEffect, useRef, useState, useCallback } from "react";
import { AudioServiceManager } from "../services/AudioServiceManager";

export function useAudio() {
	const serviceRef = useRef<AudioServiceManager | null>(null);
	const [isRecording, setIsRecording] = useState(false);
	const [isPlaying, setIsPlaying] = useState(false);
	const [isInitialized, setIsInitialized] = useState(false);

	// Single useEffect for initialization
	useEffect(() => {
		serviceRef.current = new AudioServiceManager();

		const init = async () => {
			try {
				await serviceRef.current!.initialize();
				setIsInitialized(true);
			} catch (error) {
				console.error("Failed to initialize audio service:", error);
				serviceRef.current = null;
			}
		};

		init();

		return () => {
			serviceRef.current?.cleanup();
			serviceRef.current = null;
		};
	}, []);

	const startRecording = useCallback(
		async (onChunk?: (base64: string) => void) => {
			if (!serviceRef.current || !isInitialized) {
				throw new Error("Audio not initialized");
			}

			await serviceRef.current.startRecording(onChunk);
			setIsRecording(true);
		},
		[isInitialized]
	);

	const stopRecording = useCallback(async (): Promise<string> => {
		if (!serviceRef.current) {
			throw new Error("Recorder not initialized");
		}

		const result = await serviceRef.current.stopRecording();
		setIsRecording(false);
		return result;
	}, []);

	const playAudio = useCallback(
		async (base64Audio: string) => {
			if (!serviceRef.current || !isInitialized) {
				throw new Error("Audio player not initialized");
			}

			setIsPlaying(true);
			try {
				await serviceRef.current.playAudio(base64Audio);
			} finally {
				setIsPlaying(false);
			}
		},
		[isInitialized]
	);

	const playPCMAudio = useCallback(async (base64PCM: string) => {
		if (!serviceRef.current) {
			throw new Error("Audio service not initialized");
		}

		setIsPlaying(true);
		try {
			await serviceRef.current.playPCMAudio(base64PCM);
		} catch (error) {
			console.error("Error in playPCMChunk:", error);
			throw error;
		} finally {
			setIsPlaying(false);
		}
	}, []);

	const playPCMChunks = useCallback(async (base64Chunks: string[]) => {
		if (!serviceRef.current) {
			throw new Error("Audio service not initialized");
		}

		setIsPlaying(true);
		try {
			await serviceRef.current.playPCMChunks(base64Chunks);
		} catch (error) {
			console.error("Error in playPCMChunks:", error);
			throw error;
		} finally {
			setIsPlaying(false);
		}
	}, []);

	// Update isRecording state based on service
	useEffect(() => {
		if (!serviceRef.current || !isInitialized) {
			return;
		}

		const interval = setInterval(() => {
			const recording = serviceRef.current?.isRecording() ?? false;
			setIsRecording(recording);
		}, 100); // Check every 100ms

		return () => clearInterval(interval);
	}, [isInitialized]);

	return {
		isInitialized,
		isRecording,
		isPlaying,
		startRecording,
		stopRecording,
		playAudio,
		playPCMAudio,
		playPCMChunks,
	};
}
