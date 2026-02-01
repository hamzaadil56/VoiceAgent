export interface SilenceDetectionConfig {
	threshold: number; // Volume threshold (0-1, default 0.01)
	silenceDuration: number; // Duration in ms before triggering (default 2000ms)
	checkInterval: number; // How often to check in ms (default 100ms)
}

export interface SilenceDetectionCallbacks {
	onSilenceDetected?: () => void;
	onVolumeChange?: (volume: number) => void;
}

export class SilenceDetectionService {
	private audioContext: AudioContext | null = null;
	private analyser: AnalyserNode | null = null;
	private microphone: MediaStreamAudioSourceNode | null = null;
	private stream: MediaStream | null = null;
	private isMonitoring = false;
	private silenceStartTime: number | null = null;
	private checkIntervalId: number | null = null;
	private config: SilenceDetectionConfig;
	private callbacks: SilenceDetectionCallbacks;

	constructor(
		config: Partial<SilenceDetectionConfig> = {},
		callbacks: SilenceDetectionCallbacks = {}
	) {
		this.config = {
			threshold: config.threshold ?? 0.01,
			silenceDuration: config.silenceDuration ?? 2000,
			checkInterval: config.checkInterval ?? 100,
		};
		this.callbacks = callbacks;
	}

	async initialize(stream: MediaStream): Promise<void> {
		try {
			this.stream = stream;
			this.audioContext = new (window.AudioContext ||
				(window as any).webkitAudioContext)();
			this.analyser = this.audioContext.createAnalyser();
			this.analyser.fftSize = 256;
			this.analyser.smoothingTimeConstant = 0.8;

			this.microphone = this.audioContext.createMediaStreamSource(stream);
			this.microphone.connect(this.analyser);

			console.log("✅ Silence detection initialized");
		} catch (error) {
			throw new Error(`Failed to initialize silence detection: ${error}`);
		}
	}

	startMonitoring(): void {
		if (!this.analyser || this.isMonitoring) {
			return;
		}

		this.isMonitoring = true;
		this.silenceStartTime = null;

		const dataArray = new Uint8Array(this.analyser.frequencyBinCount);

		const checkVolume = () => {
			if (!this.isMonitoring || !this.analyser) {
				return;
			}

			this.analyser.getByteFrequencyData(dataArray);

			// Calculate average volume
			let sum = 0;
			for (let i = 0; i < dataArray.length; i++) {
				sum += dataArray[i];
			}
			const averageVolume = sum / dataArray.length / 255; // Normalize to 0-1

			// Notify volume change
			this.callbacks.onVolumeChange?.(averageVolume);

			// Check if volume is below threshold
			if (averageVolume < this.config.threshold) {
				// Start or continue silence timer
				const now = Date.now();
				if (this.silenceStartTime === null) {
					this.silenceStartTime = now;
					console.log("🔇 Silence detected, starting timer...");
				} else {
					const silenceDuration = now - this.silenceStartTime;
					if (silenceDuration >= this.config.silenceDuration) {
						console.log(
							`🔇 Silence duration exceeded (${silenceDuration}ms), triggering stop`
						);
						this.callbacks.onSilenceDetected?.();
						this.stopMonitoring();
					}
				}
			} else {
				// Reset silence timer if volume is above threshold
				if (this.silenceStartTime !== null) {
					console.log("🔊 Sound detected, resetting silence timer");
					this.silenceStartTime = null;
				}
			}
		};

		// Start checking at regular intervals
		this.checkIntervalId = window.setInterval(
			checkVolume,
			this.config.checkInterval
		);
	}

	stopMonitoring(): void {
		if (!this.isMonitoring) {
			return;
		}

		this.isMonitoring = false;
		this.silenceStartTime = null;

		if (this.checkIntervalId !== null) {
			clearInterval(this.checkIntervalId);
			this.checkIntervalId = null;
		}

		console.log("⏹️ Silence detection stopped");
	}

	updateConfig(config: Partial<SilenceDetectionConfig>): void {
		this.config = { ...this.config, ...config };
	}

	updateCallbacks(callbacks: Partial<SilenceDetectionCallbacks>): void {
		this.callbacks = { ...this.callbacks, ...callbacks };
	}

	isActive(): boolean {
		return this.isMonitoring;
	}

	cleanup(): void {
		this.stopMonitoring();

		if (this.microphone) {
			this.microphone.disconnect();
			this.microphone = null;
		}

		if (this.analyser) {
			this.analyser.disconnect();
			this.analyser = null;
		}

		if (this.audioContext && this.audioContext.state !== "closed") {
			this.audioContext.close();
			this.audioContext = null;
		}

		if (this.stream) {
			this.stream.getTracks().forEach((t) => t.stop());
			this.stream = null;
		}
	}
}

