import { createFileRoute } from '@tanstack/react-router'
import Typography from '@mui/material/Typography'

export const Route = createFileRoute('/runs')({
  component: RunsPage,
})

function RunsPage() {
  return <Typography variant="h4">Runs</Typography>
}
