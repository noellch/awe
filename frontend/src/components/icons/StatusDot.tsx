import type { CSSProperties } from 'react'

type Status = 'running' | 'completed' | 'failed' | 'pending' | 'retrying'

interface StatusDotProps {
  status: Status
  size?: number
}

const statusColors: Record<Status, string> = {
  running: '#3B82F6',
  completed: '#10B981',
  failed: '#EF4444',
  pending: '#9CA3AF',
  retrying: '#F59E0B',
}

const breatheKeyframes = `
@keyframes statusBreathe {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
`

const spinKeyframes = `
@keyframes statusSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
`

export default function StatusDot({ status, size = 8 }: StatusDotProps) {
  const color = statusColors[status]

  const svgStyle: CSSProperties =
    status === 'retrying'
      ? { animation: 'statusSpin 1s linear infinite' }
      : {}

  const circleStyle: CSSProperties =
    status === 'running'
      ? { animation: 'statusBreathe 1.5s ease-in-out infinite' }
      : {}

  return (
    <>
      <style>{breatheKeyframes}{spinKeyframes}</style>
      <svg
        width={size}
        height={size}
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={svgStyle}
      >
        {status === 'running' && (
          <circle cx="8" cy="8" r="6" fill={color} style={circleStyle} />
        )}

        {status === 'completed' && (
          <>
            <circle cx="8" cy="8" r="6" fill={color} />
            <path
              d="M5.5 8L7.2 9.7L10.5 6.3"
              stroke="white"
              strokeWidth={1.5}
              strokeLinecap="round"
              strokeLinejoin="round"
              fill="none"
            />
          </>
        )}

        {status === 'failed' && (
          <>
            <circle cx="8" cy="8" r="6" fill={color} />
            <path
              d="M6 6L10 10M10 6L6 10"
              stroke="white"
              strokeWidth={1.5}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </>
        )}

        {status === 'pending' && (
          <circle
            cx="8"
            cy="8"
            r="5.25"
            stroke={color}
            strokeWidth={1.5}
            fill="none"
          />
        )}

        {status === 'retrying' && (
          <path
            d="M8 3A5 5 0 1 1 3.5 6.5M3.5 3v3.5H7"
            stroke={color}
            strokeWidth={1.5}
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
          />
        )}
      </svg>
    </>
  )
}
