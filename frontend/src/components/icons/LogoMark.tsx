interface LogoMarkProps {
  size?: number
  color?: string
}

export default function LogoMark({
  size = 20,
  color = 'currentColor',
}: LogoMarkProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 20 20"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M10 1L18 10L10 19L2 10L10 1Z"
        stroke={color}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <path
        d="M10 5L14.5 10L10 15L5.5 10L10 5Z"
        fill={color}
        opacity={0.2}
      />
    </svg>
  )
}
