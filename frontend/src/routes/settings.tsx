import { createRoute } from '@tanstack/react-router'
import Typography from '@mui/material/Typography'
import { Route as rootRoute } from './__root'

export const Route = createRoute({
  getParentRoute: () => rootRoute,
  path: '/settings',
  component: SettingsPage,
})

function SettingsPage() {
  return <Typography variant="h4">Settings</Typography>
}
