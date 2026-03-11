interface MiniFlowPreviewProps {
  stepCount: number
}

export default function MiniFlowPreview({ stepCount }: MiniFlowPreviewProps) {
  const count = Math.max(stepCount, 1)
  const circleRadius = 4
  const gap = 32
  const totalWidth = (count - 1) * gap
  const svgWidth = totalWidth + circleRadius * 2 + 2

  return (
    <svg
      width={svgWidth}
      height={80}
      viewBox={`0 0 ${svgWidth} 80`}
      style={{ display: 'block', margin: '0 auto' }}
    >
      {Array.from({ length: count }).map((_, i) => {
        const cx = circleRadius + 1 + i * gap
        const cy = 40
        return (
          <g key={i}>
            {i < count - 1 && (
              <line
                x1={cx + circleRadius}
                y1={cy}
                x2={cx + gap - circleRadius}
                y2={cy}
                stroke="#E5E7EB"
                strokeWidth={1.5}
              />
            )}
            <circle
              cx={cx}
              cy={cy}
              r={circleRadius}
              fill="#9CA3AF"
            />
          </g>
        )
      })}
    </svg>
  )
}
