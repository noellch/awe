import { createFileRoute } from '@tanstack/react-router'
import Typography from '@mui/material/Typography'

export const Route = createFileRoute('/pipelines/$pipelineId')({
  component: CanvasPage,
})

function CanvasPage() {
  const { pipelineId } = Route.useParams()
  return <Typography variant="h4">Canvas - Pipeline {pipelineId}</Typography>
}
