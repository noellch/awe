import { createRoute } from '@tanstack/react-router'
import Typography from '@mui/material/Typography'
import { Route as rootRoute } from './__root'

export const Route = createRoute({
  getParentRoute: () => rootRoute,
  path: '/pipelines',
  component: PipelinesPage,
})

function PipelinesPage() {
  return <Typography variant="h4">Pipelines</Typography>
}
