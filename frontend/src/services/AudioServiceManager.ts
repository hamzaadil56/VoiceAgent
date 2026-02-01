import { AudioRecorder } from "../utils/audioRecorder";
import { AudioPlayer } from "../utils/audioPlayer";
import {
	SilenceDetectionService,
	SilenceDetectionConfig,
} from "./SilenceDetectionService";

export interface AudioServiceCallbacks {
	onSilenceDetected?: () => void;
	onVolumeChange?: (volume: number) => void; // 0–1 normalized mic amplitude
}

export class AudioServiceManager {
	private recorder: AudioRecorder | null = null;
	private player: AudioPlayer | null = null;
	private silenceDetection: SilenceDetectionService | null = null;
	private isInitialized = false;
	private callbacks: AudioServiceCallbacks = {};
	private silenceConfig: Partial<SilenceDetectionConfig> = {};

	async initialize(): Promise<void> {
		if (this.isInitialized) {
			return;
		}

		try {
			// Create instances
			this.recorder = new AudioRecorder();
			this.player = new AudioPlayer();

			// Initialize asynchronously
			await this.recorder.initialize();
			await this.player.initialize();

			// Initialize silence detection with the recorder's stream
			const stream = this.recorder.getStream();
			if (stream) {
				this.silenceDetection = new SilenceDetectionService(
					this.silenceConfig,
					{
						onSilenceDetected: () => {
							this.callbacks.onSilenceDetected?.();
						},
						onVolumeChange: (vol) => {
							this.callbacks.onVolumeChange?.(vol);
						},
					}
				);
				await this.silenceDetection.initialize(stream);
			}

			this.isInitialized = true;
		} catch (error) {
			console.error("Failed to initialize audio service:", error);
			// Cleanup on failure
			this.cleanup();
			throw error;
		}
	}

	getRecorder(): AudioRecorder {
		if (!this.recorder || !this.isInitialized) {
			throw new Error("Audio service not initialized");
		}
		return this.recorder;
	}

	getPlayer(): AudioPlayer {
		if (!this.player || !this.isInitialized) {
			throw new Error("Audio service not initialized");
		}
		return this.player;
	}

	isServiceInitialized(): boolean {
		return this.isInitialized;
	}

	async startRecording(onChunk?: (base64: string) => void): Promise<void> {
		const recorder = this.getRecorder();

		const onChunkWrapper = async (blob: Blob) => {
			if (onChunk) {
				const base64 = await recorder.blobToBase64(blob);
				onChunk(base64);
			}
		};

		recorder.startRecording(onChunkWrapper);

		// Start silence detection monitoring
		if (this.silenceDetection) {
			this.silenceDetection.startMonitoring();
		}
	}

	async stopRecording(): Promise<string> {
		const recorder = this.getRecorder();

		// Stop silence detection monitoring
		if (this.silenceDetection) {
			this.silenceDetection.stopMonitoring();
		}

		const blob = await recorder.stopRecording();
		return await recorder.blobToBase64(blob);
	}

	async playAudio(base64Audio: string): Promise<void> {
		const player = this.getPlayer();
		await player.playChunk(base64Audio);
	}

	async playPCMAudio(base64PCM: string): Promise<void> {
		// Ensure player instance exists
		if (!this.player) {
			console.log(
				"⚠️ AudioPlayer not initialized yet, creating instance..."
			);
			this.player = new AudioPlayer();
		}

		// playPCMChunk will handle audioContext initialization if needed
		await this.player.playPCMChunk(base64PCM);
	}

	async playPCMChunks(base64Chunks: string[]): Promise<void> {
		// Ensure player instance exists
		if (!this.player) {
			console.log(
				"⚠️ AudioPlayer not initialized yet, creating instance..."
			);
			this.player = new AudioPlayer();
		}

		await this.player.playPCMChunks(base64Chunks);
	}

	isRecording(): boolean {
		return this.recorder?.isRecording() ?? false;
	}

	setSilenceConfig(config: Partial<SilenceDetectionConfig>): void {
		this.silenceConfig = { ...this.silenceConfig, ...config };
		if (this.silenceDetection) {
			this.silenceDetection.updateConfig(config);
		}
	}

	setCallbacks(callbacks: AudioServiceCallbacks): void {
		this.callbacks = { ...this.callbacks, ...callbacks };
		if (this.silenceDetection) {
			this.silenceDetection.updateCallbacks({
				onSilenceDetected: callbacks.onSilenceDetected,
				onVolumeChange: callbacks.onVolumeChange,
			});
		}
	}

	cleanup(): void {
		if (this.silenceDetection) {
			this.silenceDetection.cleanup();
			this.silenceDetection = null;
		}
		if (this.recorder) {
			this.recorder.cleanup();
			this.recorder = null;
		}
		if (this.player) {
			this.player.cleanup();
			this.player = null;
		}
		this.isInitialized = false;
	}
}
