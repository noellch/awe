import { createFileRoute } from '@tanstack/react-router'
import Typography from '@mui/material/Typography'

export const Route = createFileRoute('/agents')({
  component: AgentsPage,
})

function AgentsPage() {
  return <Typography variant="h4">Agents</Typography>
}
