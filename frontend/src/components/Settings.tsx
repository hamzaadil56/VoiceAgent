import { useState, useEffect } from 'react'

interface SettingsData {
  agent_name: string
  tts_voice: string
  temperature: number
  max_tokens: number
  stt_model: string
  llm_model: string
}

const AVAILABLE_VOICES = ['tara', 'leah', 'jess', 'leo', 'dan', 'mia', 'zac', 'zoe']

export default function Settings() {
  const [settings, setSettings] = useState<SettingsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/settings')
      if (response.ok) {
        const data = await response.json()
        setSettings(data)
      } else {
        setMessage({ type: 'error', text: 'Failed to load settings' })
      }
    } catch (error) {
      console.error('Error fetching settings:', error)
      setMessage({ type: 'error', text: 'Failed to connect to server' })
    } finally {
      setLoading(false)
    }
  }

  const fetchVoices = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/voices')
      if (response.ok) {
        const data = await response.json()
        return data.voices
      }
    } catch (error) {
      console.error('Error fetching voices:', error)
    }
    return AVAILABLE_VOICES
  }

  const handleSave = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setSaving(true)
    setMessage(null)

    const formData = new FormData(e.currentTarget)
    const updates: Partial<SettingsData> = {}

    if (formData.get('agent_name')) {
      updates.agent_name = formData.get('agent_name') as string
    }
    if (formData.get('tts_voice')) {
      updates.tts_voice = formData.get('tts_voice') as string
    }
    if (formData.get('temperature')) {
      updates.temperature = parseFloat(formData.get('temperature') as string)
    }
    if (formData.get('max_tokens')) {
      updates.max_tokens = parseInt(formData.get('max_tokens') as string)
    }

    try {
      const response = await fetch('http://localhost:8000/api/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      })

      if (response.ok) {
        const data = await response.json()
        setSettings(data.settings)
        setMessage({ type: 'success', text: 'Settings updated successfully!' })
      } else {
        setMessage({ type: 'error', text: 'Failed to update settings' })
      }
    } catch (error) {
      console.error('Error updating settings:', error)
      setMessage({ type: 'error', text: 'Failed to connect to server' })
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 text-center">
        <p className="text-white">Loading settings...</p>
      </div>
    )
  }

  if (!settings) {
    return (
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 text-center">
        <p className="text-red-300">Failed to load settings</p>
        <button
          onClick={fetchSettings}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8">
      <h2 className="text-2xl font-bold text-white mb-6">Settings</h2>

      {message && (
        <div
          className={`mb-4 p-3 rounded-lg ${
            message.type === 'success'
              ? 'bg-green-500/20 text-green-200'
              : 'bg-red-500/20 text-red-200'
          }`}
        >
          {message.text}
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        <div>
          <label className="block text-white font-semibold mb-2">
            Agent Name
          </label>
          <input
            type="text"
            name="agent_name"
            defaultValue={settings.agent_name}
            className="w-full px-4 py-2 bg-white/20 text-white rounded-lg border border-white/30 focus:outline-none focus:ring-2 focus:ring-white/50"
          />
        </div>

        <div>
          <label className="block text-white font-semibold mb-2">
            TTS Voice
          </label>
          <select
            name="tts_voice"
            defaultValue={settings.tts_voice}
            className="w-full px-4 py-2 bg-white/20 text-white rounded-lg border border-white/30 focus:outline-none focus:ring-2 focus:ring-white/50"
          >
            {AVAILABLE_VOICES.map((voice) => (
              <option key={voice} value={voice} className="bg-gray-800">
                {voice}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-white font-semibold mb-2">
            Temperature ({settings.temperature})
          </label>
          <input
            type="range"
            name="temperature"
            min="0"
            max="1"
            step="0.1"
            defaultValue={settings.temperature}
            className="w-full"
          />
          <p className="text-white/60 text-sm mt-1">
            Controls randomness (0.0 = deterministic, 1.0 = creative)
          </p>
        </div>

        <div>
          <label className="block text-white font-semibold mb-2">
            Max Tokens
          </label>
          <input
            type="number"
            name="max_tokens"
            min="100"
            max="2000"
            step="100"
            defaultValue={settings.max_tokens}
            className="w-full px-4 py-2 bg-white/20 text-white rounded-lg border border-white/30 focus:outline-none focus:ring-2 focus:ring-white/50"
          />
        </div>

        <div className="bg-white/5 rounded-lg p-4">
          <h3 className="text-white font-semibold mb-2">Model Information</h3>
          <div className="text-white/80 text-sm space-y-1">
            <p>STT Model: {settings.stt_model}</p>
            <p>LLM Model: {settings.llm_model}</p>
          </div>
        </div>

        <button
          type="submit"
          disabled={saving}
          className="w-full px-6 py-3 bg-purple-500 hover:bg-purple-600 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition-all"
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </form>
    </div>
  )
}



