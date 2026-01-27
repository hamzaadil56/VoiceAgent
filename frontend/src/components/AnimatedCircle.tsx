import { AgentState } from '../hooks/useWebSocket'

interface AnimatedCircleProps {
  state: AgentState
  size?: number
  onClick?: () => void
}

export default function AnimatedCircle({ state, size = 200, onClick }: AnimatedCircleProps) {
  const getCircleClasses = () => {
    const baseClasses = 'rounded-full transition-all duration-500 ease-out relative overflow-hidden'
    
    switch (state) {
      case 'idle':
        return `${baseClasses} glass border-2 border-border`
      case 'listening':
        return `${baseClasses} border-2 border-accent-primary shadow-lg shadow-accent-primary/50 animate-pulse`
      case 'processing':
        return `${baseClasses} border-2 border-accent-tertiary shadow-lg shadow-accent-tertiary/50 animate-spin-slow`
      case 'speaking':
        return `${baseClasses} border-2 border-success shadow-lg shadow-success/50 animate-pulse-slow`
      case 'connected':
        return `${baseClasses} glass border-2 border-success/50`
      case 'disconnected':
        return `${baseClasses} glass border-2 border-error/50 opacity-50`
      default:
        return `${baseClasses} glass border-2 border-border`
    }
  }

  const getBackgroundGradient = () => {
    switch (state) {
      case 'listening':
        return 'bg-gradient-to-br from-accent-primary/20 to-accent-secondary/20'
      case 'processing':
        return 'bg-gradient-to-br from-accent-tertiary/20 to-accent-primary/20'
      case 'speaking':
        return 'bg-gradient-to-br from-success/20 to-accent-secondary/20'
      default:
        return 'bg-surface'
    }
  }

  const getInnerCircleClasses = () => {
    const baseClasses = 'rounded-full absolute transition-all duration-500'
    
    switch (state) {
      case 'listening':
        return `${baseClasses} bg-accent-primary/30 animate-ping`
      case 'processing':
        return `${baseClasses} bg-accent-tertiary/30 animate-spin-slow`
      case 'speaking':
        return `${baseClasses} bg-success/30 animate-pulse`
      default:
        return `${baseClasses} bg-transparent`
    }
  }

  const getIcon = () => {
    switch (state) {
      case 'idle':
        return (
          <svg className="w-16 h-16 text-accent-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        )
      case 'listening':
        return (
          <svg className="w-16 h-16 text-accent-primary animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10a4 4 0 11-8 0 4 4 0 018 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.5 10a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
      case 'processing':
        return (
          <svg className="w-16 h-16 text-accent-tertiary animate-spin-slow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        )
      case 'speaking':
        return (
          <svg className="w-16 h-16 text-success animate-pulse-slow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 14.142M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
          </svg>
        )
      case 'connected':
        return (
          <svg className="w-16 h-16 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
      case 'disconnected':
        return (
          <svg className="w-16 h-16 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
      default:
        return (
          <svg className="w-16 h-16 text-accent-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        )
    }
  }

  return (
    <div 
      className={`relative flex items-center justify-center ${onClick ? 'cursor-pointer group' : ''}`}
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
        className={`${getCircleClasses()} ${onClick ? 'hover:scale-105 active:scale-95 hover:shadow-glow-strong' : ''}`}
        style={{
          width: `${size}px`,
          height: `${size}px`,
        }}
      >
        {/* Background gradient layer */}
        <div className={`absolute inset-0 ${getBackgroundGradient()} rounded-full`} />
        
        {/* Inner circle for layered animation */}
        {state !== 'idle' && state !== 'connected' && state !== 'disconnected' && (
          <div 
            className={getInnerCircleClasses()} 
            style={{
              width: `${size * 0.7}px`,
              height: `${size * 0.7}px`,
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
            }}
          />
        )}
        
        {/* Icon */}
        <div className="absolute inset-0 flex items-center justify-center z-10">
          {getIcon()}
        </div>
      </div>
      
      {/* Ripple effects for listening and speaking */}
      {(state === 'listening' || state === 'speaking') && (
        <>
          <div
            className={`absolute rounded-full border-2 ${
              state === 'listening' ? 'border-accent-primary/50' : 'border-success/50'
            } animate-ping`}
            style={{
              width: `${size + 50}px`,
              height: `${size + 50}px`,
              animationDelay: '0.2s',
            }}
          />
          <div
            className={`absolute rounded-full border-2 ${
              state === 'listening' ? 'border-accent-secondary/40' : 'border-accent-secondary/40'
            } animate-ping`}
            style={{
              width: `${size + 100}px`,
              height: `${size + 100}px`,
              animationDelay: '0.4s',
            }}
          />
          <div
            className={`absolute rounded-full border ${
              state === 'listening' ? 'border-accent-primary/30' : 'border-success/30'
            } animate-ping`}
            style={{
              width: `${size + 150}px`,
              height: `${size + 150}px`,
              animationDelay: '0.6s',
            }}
          />
        </>
      )}
    </div>
  )
}



