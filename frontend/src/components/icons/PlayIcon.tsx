interface PlayIconProps {
  size?: number
  color?: string
}

export default function PlayIcon({
  size = 16,
  color = 'currentColor',
}: PlayIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M4 3L13 8L4 13V3Z"
        stroke={color}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  )
}
