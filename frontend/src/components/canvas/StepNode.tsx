import { Handle, Position, type Node, type NodeProps } from '@xyflow/react'
import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'
import StatusDot from '../icons/StatusDot'

export interface StepNodeData extends Record<string, unknown> {
  label: string
  agent: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'retrying'
}

export type StepNodeType = Node<StepNodeData, 'step'>

export default function StepNode({ data, selected }: NodeProps<StepNodeType>) {
  return (
    <Box
      sx={{
        width: 160,
        height: 56,
        borderRadius: '8px',
        border: selected ? '2px solid #3B82F6' : '1px solid #E5E7EB',
        boxShadow: selected ? '0 0 0 2px rgba(59,130,246,0.1)' : 'none',
        background: '#fff',
        display: 'flex',
        alignItems: 'center',
        gap: 1,
        px: 1.5,
        cursor: 'pointer',
        boxSizing: 'border-box',
      }}
    >
      <Handle
        type="target"
        position={Position.Left}
        style={{
          width: 6,
          height: 6,
          background: '#9CA3AF',
          border: '2px solid white',
          borderRadius: '50%',
        }}
      />
      <StatusDot status={data.status} size={8} />
      <Box sx={{ minWidth: 0, flex: 1 }}>
        <Typography
          sx={{
            fontWeight: 600,
            fontSize: 13,
            lineHeight: 1.3,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {data.label}
        </Typography>
        <Typography
          sx={{
            color: '#9CA3AF',
            fontSize: 11,
            lineHeight: 1.3,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {data.agent}
        </Typography>
      </Box>
      <Handle
        type="source"
        position={Position.Right}
        style={{
          width: 6,
          height: 6,
          background: '#9CA3AF',
          border: '2px solid white',
          borderRadius: '50%',
        }}
      />
    </Box>
  )
}
