import { createRoute } from '@tanstack/react-router'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'
import Grid from '@mui/material/Grid'
import Button from '@mui/material/Button'
import Chip from '@mui/material/Chip'
import Skeleton from '@mui/material/Skeleton'
import Card from '@mui/material/Card'
import { Route as rootRoute } from './__root'
import { usePipelines } from '../api/hooks'
import PipelineCard from '../components/pipeline/PipelineCard'

export const Route = createRoute({
  getParentRoute: () => rootRoute,
  path: '/pipelines',
  component: PipelinesPage,
})

function PipelinesPage() {
  const { data: pipelines, isLoading, isError } = usePipelines()

  return (
    <Box sx={{ p: 3, bgcolor: 'background.default', minHeight: '100%' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            Pipelines
          </Typography>
          {pipelines && (
            <Chip label={pipelines.length} size="small" />
          )}
        </Box>
        <Button variant="text">+ New Pipeline</Button>
      </Box>

      {/* Loading */}
      {isLoading && (
        <Grid container spacing={3}>
          {[0, 1, 2].map((i) => (
            <Grid size={{ xs: 12, sm: 6, md: 4, xl: 3 }} key={i}>
              <Card variant="outlined" sx={{ borderRadius: '8px' }}>
                <Skeleton variant="rectangular" height={80} />
                <Box sx={{ p: 2 }}>
                  <Skeleton width="60%" height={24} />
                  <Skeleton width="40%" height={20} sx={{ mt: 1 }} />
                  <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
                    <Skeleton width={60} height={36} />
                    <Skeleton width={60} height={36} />
                  </Box>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Error */}
      {isError && (
        <Typography color="error" sx={{ mt: 4, textAlign: 'center' }}>
          Failed to load pipelines.
        </Typography>
      )}

      {/* Empty */}
      {pipelines && pipelines.length === 0 && (
        <Box sx={{ textAlign: 'center', mt: 10 }}>
          <Typography variant="h6" color="text.secondary">
            尚無 Pipeline
          </Typography>
          <Typography color="text.secondary" sx={{ mt: 1 }}>
            建立第一個 Pipeline
          </Typography>
          <Button variant="text" sx={{ mt: 2 }}>+ New Pipeline</Button>
        </Box>
      )}

      {/* Data */}
      {pipelines && pipelines.length > 0 && (
        <Grid container spacing={3}>
          {pipelines.map((pipeline) => (
            <Grid size={{ xs: 12, sm: 6, md: 4, xl: 3 }} key={pipeline.name}>
              <PipelineCard pipeline={pipeline} />
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  )
}
