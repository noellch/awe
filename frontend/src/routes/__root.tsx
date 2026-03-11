import { createRootRoute, Outlet } from '@tanstack/react-router'
import Box from '@mui/material/Box'
import TopNav from '../components/layout/TopNav'

export const Route = createRootRoute({
  component: RootLayout,
})

function RootLayout() {
  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <TopNav />
      <Box
        component="main"
        sx={{
          flex: 1,
          mt: '48px',
          p: 3,
          backgroundColor: 'background.default',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  )
}
