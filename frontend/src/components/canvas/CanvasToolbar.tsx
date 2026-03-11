import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button'
import PlayIcon from '../icons/PlayIcon'

interface CanvasToolbarProps {
  pipelineName: string
}

export default function CanvasToolbar({ pipelineName }: CanvasToolbarProps) {
  return (
    <Box
      sx={{
        height: 48,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        px: 2,
        borderBottom: '1px solid #E5E7EB',
        background: '#fff',
        flexShrink: 0,
      }}
    >
      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
        {pipelineName}
      </Typography>
      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
        <Button variant="text" disabled>
          Save
        </Button>
        <Button
          variant="contained"
          size="small"
          startIcon={<PlayIcon size={14} />}
        >
          Run
        </Button>
      </Box>
    </Box>
  )
}
