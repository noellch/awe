import { useNavigate, useMatches } from '@tanstack/react-router'
import AppBar from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar'
import Tabs from '@mui/material/Tabs'
import Tab from '@mui/material/Tab'
import Box from '@mui/material/Box'
import IconButton from '@mui/material/IconButton'
import Typography from '@mui/material/Typography'
import SettingsIcon from '@mui/icons-material/Settings'
import LogoMark from '../icons/LogoMark'

const navTabs = [
  { label: 'Pipelines', path: '/pipelines' },
  { label: 'Runs', path: '/runs' },
  { label: 'Agents', path: '/agents' },
] as const

export default function TopNav() {
  const navigate = useNavigate()
  const matches = useMatches()

  const currentPath = matches[matches.length - 1]?.pathname ?? '/'
  const activeIndex = navTabs.findIndex((tab) =>
    currentPath.startsWith(tab.path),
  )

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        height: 48,
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E5E7EB',
      }}
    >
      <Toolbar
        sx={{
          minHeight: '48px !important',
          height: 48,
          px: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        {/* Left: Logo */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <LogoMark size={20} color="#3B82F6" />
          <Typography
            variant="subtitle1"
            sx={{
              fontWeight: 700,
              color: '#111827',
              letterSpacing: '0.05em',
            }}
          >
            AWE
          </Typography>
        </Box>

        {/* Center: Tabs */}
        <Tabs
          value={activeIndex === -1 ? false : activeIndex}
          onChange={(_, newValue: number) => {
            void navigate({ to: navTabs[newValue].path })
          }}
          sx={{
            minHeight: 48,
            '& .MuiTab-root': {
              minHeight: 48,
              textTransform: 'none',
              fontSize: '0.875rem',
              fontWeight: 500,
              color: '#6B7280',
              '&.Mui-selected': {
                color: '#3B82F6',
              },
            },
            '& .MuiTabs-indicator': {
              height: 2,
              backgroundColor: '#3B82F6',
            },
          }}
        >
          {navTabs.map((tab) => (
            <Tab key={tab.path} label={tab.label} />
          ))}
        </Tabs>

        {/* Right: Settings */}
        <IconButton
          size="small"
          onClick={() => void navigate({ to: '/settings' })}
          sx={{ color: '#6B7280' }}
        >
          <SettingsIcon fontSize="small" />
        </IconButton>
      </Toolbar>
    </AppBar>
  )
}
