import type { Node } from '@xyflow/react'
import Box from '@mui/material/Box'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import TextField from '@mui/material/TextField'
import IconButton from '@mui/material/IconButton'
import CloseIcon from '@mui/icons-material/Close'
import type { StepNodeData } from './StepNode'

interface NodeConfigPanelProps {
  selectedNode: Node<StepNodeData> | null
  onClose: () => void
}

export default function NodeConfigPanel({
  selectedNode,
  onClose,
}: NodeConfigPanelProps) {
  const isOpen = selectedNode !== null

  return (
    <Box
      sx={{
        width: isOpen ? 320 : 0,
        opacity: isOpen ? 1 : 0,
        overflow: 'hidden',
        transition: 'width 150ms ease, opacity 150ms ease',
        borderLeft: '1px solid #E5E7EB',
        background: '#fff',
        height: '100%',
        flexShrink: 0,
      }}
    >
      {selectedNode && (
        <Box sx={{ width: 320, height: '100%', display: 'flex', flexDirection: 'column' }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              px: 2,
              py: 1.5,
              borderBottom: '1px solid #E5E7EB',
            }}
          >
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              {selectedNode.data.label}
            </Typography>
            <IconButton size="small" onClick={onClose}>
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>
          <Stack spacing={2} sx={{ p: 2, flex: 1, overflow: 'auto' }}>
            <TextField
              label="Step ID"
              value={selectedNode.data.label}
              size="small"
              fullWidth
              slotProps={{ input: { readOnly: true } }}
            />
            <TextField
              label="Agent"
              value={selectedNode.data.agent}
              size="small"
              fullWidth
              slotProps={{ input: { readOnly: true } }}
            />
            <TextField
              label="Prompt"
              value={(selectedNode.data.prompt as string) ?? ''}
              size="small"
              fullWidth
              multiline
              minRows={4}
              slotProps={{ input: { readOnly: true } }}
            />
          </Stack>
        </Box>
      )}
    </Box>
  )
}
