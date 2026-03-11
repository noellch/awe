import { createRoute } from '@tanstack/react-router'
import Typography from '@mui/material/Typography'
import { Route as rootRoute } from './__root'

export const Route = createRoute({
  getParentRoute: () => rootRoute,
  path: '/runs',
  component: RunsPage,
})

function RunsPage() {
  return <Typography variant="h4">Runs</Typography>
}
