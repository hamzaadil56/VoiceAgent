import { AgentState } from '../hooks/useWebSocket'

interface AnimatedCircleProps {
  state: AgentState
  size?: number
  onClick?: () => void
}

export default function AnimatedCircle({ state, size = 200, onClick }: AnimatedCircleProps) {
  const getCircleClasses = () => {
    const baseClasses = 'rounded-full transition-all duration-300 ease-in-out'
    
    switch (state) {
      case 'idle':
        return `${baseClasses} bg-white/20 border-4 border-white/40`
      case 'listening':
        return `${baseClasses} bg-blue-400/60 border-4 border-blue-300 animate-pulse`
      case 'processing':
        return `${baseClasses} bg-purple-400/60 border-4 border-purple-300 animate-spin-slow`
      case 'speaking':
        return `${baseClasses} bg-green-400/60 border-4 border-green-300 animate-pulse-slow`
      case 'connected':
        return `${baseClasses} bg-white/30 border-4 border-white/50`
      case 'disconnected':
        return `${baseClasses} bg-gray-400/40 border-4 border-gray-300/40`
      default:
        return `${baseClasses} bg-white/20 border-4 border-white/40`
    }
  }

  const getInnerCircleClasses = () => {
    const baseClasses = 'rounded-full absolute inset-4 transition-all duration-300'
    
    switch (state) {
      case 'listening':
        return `${baseClasses} bg-blue-500/40 animate-ping`
      case 'processing':
        return `${baseClasses} bg-purple-500/40`
      case 'speaking':
        return `${baseClasses} bg-green-500/40 animate-pulse`
      default:
        return `${baseClasses} bg-white/20`
    }
  }

  const getIcon = () => {
    switch (state) {
      case 'idle':
        return '🎙️'
      case 'listening':
        return '👂'
      case 'processing':
        return '🤔'
      case 'speaking':
        return '🗣️'
      case 'connected':
        return '✓'
      case 'disconnected':
        return '✗'
      default:
        return '🎙️'
    }
  }

  return (
    <div 
      className={`relative flex items-center justify-center ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onClick()
        }
      } : undefined}
    >
      <div
        className={`${getCircleClasses()} ${onClick ? 'hover:scale-105 active:scale-95' : ''}`}
        style={{
          width: `${size}px`,
          height: `${size}px`,
        }}
      >
        {/* Inner circle for layered animation */}
        {state !== 'idle' && state !== 'connected' && state !== 'disconnected' && (
          <div className={getInnerCircleClasses()} />
        )}
        
        {/* Icon/Text */}
        <div className="absolute inset-0 flex items-center justify-center text-4xl z-10">
          {getIcon()}
        </div>
      </div>
      
      {/* Ripple effects for listening and speaking */}
      {(state === 'listening' || state === 'speaking') && (
        <>
          <div
            className={`absolute rounded-full border-2 ${
              state === 'listening' ? 'border-blue-300' : 'border-green-300'
            } animate-ping`}
            style={{
              width: `${size + 40}px`,
              height: `${size + 40}px`,
              animationDelay: '0.2s',
            }}
          />
          <div
            className={`absolute rounded-full border-2 ${
              state === 'listening' ? 'border-blue-200' : 'border-green-200'
            } animate-ping`}
            style={{
              width: `${size + 80}px`,
              height: `${size + 80}px`,
              animationDelay: '0.4s',
            }}
          />
        </>
      )}
    </div>
  )
}



