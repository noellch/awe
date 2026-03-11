import { createRoute } from '@tanstack/react-router'
import Typography from '@mui/material/Typography'
import { Route as rootRoute } from './__root'

export const Route = createRoute({
  getParentRoute: () => rootRoute,
  path: '/pipelines/$pipelineId',
  component: CanvasPage,
})

function CanvasPage() {
  const { pipelineId } = Route.useParams()
  return <Typography variant="h4">Canvas - Pipeline {pipelineId}</Typography>
}
