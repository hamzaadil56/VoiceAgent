/** Audio recording utility using Web Audio API */

export class AudioRecorder {
  private mediaRecorder: MediaRecorder | null = null
  private audioChunks: Blob[] = []
  private stream: MediaStream | null = null
  private onChunkCallback?: (chunk: Blob) => void

  /**
   * Request microphone access and initialize recorder
   */
  async initialize(): Promise<void> {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      // Prefer WAV format, fallback to webm
      let mimeType = 'audio/webm'
      if (MediaRecorder.isTypeSupported('audio/wav')) {
        mimeType = 'audio/wav'
      } else if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        mimeType = 'audio/webm;codecs=opus'
      } else if (MediaRecorder.isTypeSupported('audio/webm')) {
        mimeType = 'audio/webm'
      }
      
      this.mediaRecorder = new MediaRecorder(this.stream, {
        mimeType,
        audioBitsPerSecond: 128000,
      })

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data)
          if (this.onChunkCallback) {
            this.onChunkCallback(event.data)
          }
        }
      }
    } catch (error) {
      throw new Error(`Failed to initialize audio recorder: ${error}`)
    }
  }

  /**
   * Start recording
   */
  startRecording(onChunk?: (chunk: Blob) => void): void {
    if (!this.mediaRecorder) {
      throw new Error('Recorder not initialized. Call initialize() first.')
    }

    this.audioChunks = []
    this.onChunkCallback = onChunk
    this.mediaRecorder.start(100) // Collect data every 100ms
  }

  /**
   * Stop recording and return audio blob
   */
  async stopRecording(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
        reject(new Error('Recorder is not recording'))
        return
      }

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' })
        resolve(audioBlob)
      }

      this.mediaRecorder.stop()
    })
  }

  /**
   * Check if currently recording
   */
  isRecording(): boolean {
    return this.mediaRecorder?.state === 'recording'
  }

  /**
   * Cleanup resources
   */
  cleanup(): void {
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop()
    }

    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop())
      this.stream = null
    }

    this.mediaRecorder = null
    this.audioChunks = []
    this.onChunkCallback = undefined
  }

  /**
   * Get the audio stream (for silence detection)
   */
  getStream(): MediaStream | null {
    return this.stream
  }

  /**
   * Convert blob to base64
   */
  async blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onloadend = () => {
        const base64 = reader.result as string
        // Remove data URL prefix
        const base64Data = base64.split(',')[1]
        resolve(base64Data)
      }
      reader.onerror = reject
      reader.readAsDataURL(blob)
    })
  }
}

