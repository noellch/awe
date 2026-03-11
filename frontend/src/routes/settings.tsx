import { createFileRoute } from '@tanstack/react-router'
import Typography from '@mui/material/Typography'

export const Route = createFileRoute('/settings')({
  component: SettingsPage,
})

function SettingsPage() {
  return <Typography variant="h4">Settings</Typography>
}
