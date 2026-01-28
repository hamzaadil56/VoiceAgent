/** Real-time PCM audio playback utility for streaming voice */

export class AudioPlayer {
	private audioContext: AudioContext | null = null;
	private sampleRate: number = 24000; // Orpheus TTS outputs at 24kHz
	private isPlaying: boolean = false;
	private playbackQueue: AudioBufferSourceNode[] = [];

	/**
	 * Initialize audio context
	 */
	async initialize(): Promise<void> {
		try {
			this.audioContext = new (window.AudioContext ||
				(window as any).webkitAudioContext)({
				sampleRate: this.sampleRate,
			});
			console.log(
				"✅ AudioPlayer initialized with sample rate:",
				this.sampleRate
			);
		} catch (error) {
			throw new Error(`Failed to initialize audio context: ${error}`);
		}
	}

	/**
	 * Play PCM audio chunk (base64 encoded Int16 PCM data)
	 * This is for real-time streaming - each chunk plays immediately
	 */
	async playPCMChunk(base64Audio: string): Promise<void> {
		if (!this.audioContext) {
			await this.initialize();
		}

		try {
			// Decode base64 to binary string
			const binaryString = atob(base64Audio);

			if (binaryString.length === 0) {
				console.warn("Empty PCM chunk received");
				return;
			}

			// Convert binary string to Uint8Array for proper byte handling
			let bytes = new Uint8Array(binaryString.length);
			for (let i = 0; i < binaryString.length; i++) {
				bytes[i] = binaryString.charCodeAt(i);
			}

			// Ensure we have an even number of bytes (Int16 = 2 bytes per sample)
			if (bytes.length % 2 !== 0) {
				console.warn(
					`PCM chunk has odd length (${bytes.length}), truncating last byte`
				);
				bytes = bytes.slice(0, bytes.length - 1);
			}

			// Convert bytes to Int16Array (little-endian PCM format from WAV)
			// WAV files store PCM as little-endian Int16: [LSB, MSB, LSB, MSB, ...]
			const sampleCount = bytes.length / 2;
			const pcmData = new Int16Array(sampleCount);

			// Use DataView for proper little-endian conversion
			const dataView = new DataView(
				bytes.buffer,
				bytes.byteOffset,
				bytes.byteLength
			);
			for (let i = 0; i < sampleCount; i++) {
				// Read as little-endian Int16 (WAV format)
				pcmData[i] = dataView.getInt16(i * 2, true); // true = little-endian
			}

			// Convert Int16 PCM to Float32 (Web Audio API format)
			const float32Data = new Float32Array(pcmData.length);
			for (let i = 0; i < pcmData.length; i++) {
				// Normalize to -1.0 to 1.0 range, clamp to prevent clipping
				const normalized = pcmData[i] / 32768.0;
				float32Data[i] = Math.max(-1.0, Math.min(1.0, normalized));
			}

			// Create audio buffer
			const audioBuffer = this.audioContext!.createBuffer(
				1, // mono
				float32Data.length,
				this.sampleRate
			);
			audioBuffer.copyToChannel(float32Data, 0);

			// Create source and play
			const source = this.audioContext!.createBufferSource();
			source.buffer = audioBuffer;
			source.connect(this.audioContext!.destination);

			// Return promise that resolves when this chunk finishes
			return new Promise((resolve, reject) => {
				source.onended = () => {
					const index = this.playbackQueue.indexOf(source);
					if (index > -1) {
						this.playbackQueue.splice(index, 1);
					}
					if (this.playbackQueue.length === 0) {
						this.isPlaying = false;
					}
					resolve();
				};

				try {
					this.playbackQueue.push(source);
					this.isPlaying = true;
					source.start(0);
				} catch (error) {
					console.error("PCM playback error:", error);
					reject(error);
				}
			});
		} catch (error) {
			console.error("Error playing PCM chunk:", error);
			throw error;
		}
	}

	/**
	 * Play multiple PCM chunks that were collected as a complete audio
	 * Decodes each base64 chunk individually and concatenates the binary data
	 */
	async playPCMChunks(base64Chunks: string[]): Promise<void> {
		if (!this.audioContext) {
			await this.initialize();
		}

		if (base64Chunks.length === 0) {
			console.warn("No PCM chunks to play");
			return;
		}

		try {
			// Decode each base64 chunk to bytes and collect all bytes
			const allBytes: Uint8Array[] = [];
			let totalLength = 0;

			for (const base64Chunk of base64Chunks) {
				try {
					const binaryString = atob(base64Chunk);
					const bytes = new Uint8Array(binaryString.length);
					for (let i = 0; i < binaryString.length; i++) {
						bytes[i] = binaryString.charCodeAt(i);
					}
					allBytes.push(bytes);
					totalLength += bytes.length;
				} catch (error) {
					console.error("Error decoding chunk:", error);
					// Skip invalid chunks
					continue;
				}
			}

			if (totalLength === 0) {
				console.warn("No valid audio data after decoding chunks");
				return;
			}

			// Concatenate all bytes into a single array
			const combinedBytes = new Uint8Array(totalLength);
			let offset = 0;
			for (const bytes of allBytes) {
				combinedBytes.set(bytes, offset);
				offset += bytes.length;
			}

			console.log(
				`Combined ${base64Chunks.length} chunks into ${combinedBytes.length} bytes`
			);

			// Ensure we have an even number of bytes (Int16 = 2 bytes per sample)
			let finalBytes = combinedBytes;
			if (finalBytes.length % 2 !== 0) {
				console.warn(
					`Combined PCM has odd length (${finalBytes.length}), truncating last byte`
				);
				finalBytes = finalBytes.slice(0, finalBytes.length - 1);
			}

			// Convert bytes to Int16Array (little-endian PCM format from WAV)
			const sampleCount = finalBytes.length / 2;
			const pcmData = new Int16Array(sampleCount);

			// Use DataView for proper little-endian conversion
			const dataView = new DataView(
				finalBytes.buffer,
				finalBytes.byteOffset,
				finalBytes.byteLength
			);
			for (let i = 0; i < sampleCount; i++) {
				// Read as little-endian Int16 (WAV format)
				pcmData[i] = dataView.getInt16(i * 2, true); // true = little-endian
			}

			// Convert Int16 PCM to Float32 (Web Audio API format)
			const float32Data = new Float32Array(pcmData.length);
			for (let i = 0; i < pcmData.length; i++) {
				// Normalize to -1.0 to 1.0 range, clamp to prevent clipping
				const normalized = pcmData[i] / 32768.0;
				float32Data[i] = Math.max(-1.0, Math.min(1.0, normalized));
			}

			// Create audio buffer
			const audioBuffer = this.audioContext!.createBuffer(
				1, // mono
				float32Data.length,
				this.sampleRate
			);
			audioBuffer.copyToChannel(float32Data, 0);

			// Create source and play
			const source = this.audioContext!.createBufferSource();
			source.buffer = audioBuffer;
			source.connect(this.audioContext!.destination);

			// Return promise that resolves when audio finishes
			return new Promise((resolve, reject) => {
				source.onended = () => {
					this.isPlaying = false;
					resolve();
				};

				try {
					this.isPlaying = true;
					source.start(0);
				} catch (error) {
					this.isPlaying = false;
					console.error("PCM chunks playback error:", error);
					reject(error);
				}
			});
		} catch (error) {
			console.error("Error playing PCM chunks:", error);
			throw error;
		}
	}

	/**
	 * Play complete WAV file (fallback for complete audio)
	 * This decodes the WAV header and plays the complete file
	 */
	async playChunk(base64Audio: string): Promise<void> {
		if (!this.audioContext) {
			await this.initialize();
		}

		try {
			// Decode base64 to ArrayBuffer
			const binaryString = atob(base64Audio);
			const bytes = new Uint8Array(binaryString.length);
			for (let i = 0; i < binaryString.length; i++) {
				bytes[i] = binaryString.charCodeAt(i);
			}

			// Decode audio data
			const audioBuffer = await this.audioContext!.decodeAudioData(
				bytes.buffer
			);

			// Create source and play
			const source = this.audioContext!.createBufferSource();
			source.buffer = audioBuffer;
			source.connect(this.audioContext!.destination);

			// Return a Promise that resolves when audio actually finishes playing
			return new Promise((resolve, reject) => {
				source.onended = () => {
					this.isPlaying = false;
					resolve();
				};

				try {
					this.isPlaying = true;
					source.start(0);
				} catch (error) {
					this.isPlaying = false;
					console.error("WAV playback error:", error);
					reject(error);
				}
			});
		} catch (error) {
			console.error("Error playing audio chunk:", error);
			throw error;
		}
	}

	/**
	 * Check if currently playing
	 */
	isCurrentlyPlaying(): boolean {
		return this.isPlaying;
	}

	/**
	 * Stop all playback
	 */
	stop(): void {
		// Stop all queued sources
		this.playbackQueue.forEach((source) => {
			try {
				source.stop();
			} catch (e) {
				// Source may already be stopped
			}
		});
		this.playbackQueue = [];
		this.isPlaying = false;
	}

	/**
	 * Cleanup resources
	 */
	cleanup(): void {
		this.stop();
		if (this.audioContext) {
			this.audioContext.close();
			this.audioContext = null;
		}
	}
}
