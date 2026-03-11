import { createFileRoute } from '@tanstack/react-router'
import Typography from '@mui/material/Typography'

export const Route = createFileRoute('/pipelines')({
  component: PipelinesPage,
})

function PipelinesPage() {
  return <Typography variant="h4">Pipelines</Typography>
}
