import Card from '@mui/material/Card'
import CardContent from '@mui/material/CardContent'
import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button'
import { useNavigate } from '@tanstack/react-router'
import PlayIcon from '../icons/PlayIcon'
import MiniFlowPreview from './MiniFlowPreview'
import type { PipelineSummary } from '../../api/hooks'

interface PipelineCardProps {
  pipeline: PipelineSummary
}

export default function PipelineCard({ pipeline }: PipelineCardProps) {
  const navigate = useNavigate()

  return (
    <Card
      variant="outlined"
      sx={{
        borderRadius: '8px',
        transition: 'border-color 150ms',
        '&:hover': {
          borderColor: '#3B82F6',
        },
      }}
    >
      <Box sx={{ py: 2, px: 2, display: 'flex', justifyContent: 'center' }}>
        <MiniFlowPreview stepCount={pipeline.step_count} />
      </Box>

      <CardContent sx={{ pt: 0 }}>
        <Typography sx={{ fontWeight: 600, fontSize: 16 }}>
          {pipeline.name}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          {pipeline.description || `${pipeline.step_count} steps`}
        </Typography>

        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
          <Button variant="contained" size="small" startIcon={<PlayIcon />}>
            Run
          </Button>
          <Button
            variant="outlined"
            size="small"
            onClick={() =>
              navigate({ to: '/pipelines/$pipelineId', params: { pipelineId: pipeline.name } })
            }
          >
            Edit
          </Button>
        </Box>
      </CardContent>
    </Card>
  )
}
