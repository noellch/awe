interface PipelineIconProps {
  size?: number
  color?: string
}

export default function PipelineIcon({
  size = 16,
  color = 'currentColor',
}: PipelineIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle cx="3" cy="8" r="2" stroke={color} strokeWidth={1.5} />
      <circle cx="8" cy="4" r="2" stroke={color} strokeWidth={1.5} />
      <circle cx="13" cy="8" r="2" stroke={color} strokeWidth={1.5} />
      <path
        d="M5 8L6 5.5M10 5.5L11 8"
        stroke={color}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
