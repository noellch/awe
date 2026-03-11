import { createTheme } from '@mui/material/styles'

// AWE Design System Colors
const colors = {
  surface: {
    primary: '#FFFFFF',
    secondary: '#F9FAFB',
    variant: '#F3F4F6',
  },
  border: {
    default: '#E5E7EB',
  },
  text: {
    primary: '#111827',
    secondary: '#6B7280',
  },
  accent: '#3B82F6',
  status: {
    running: '#3B82F6',
    completed: '#10B981',
    failed: '#EF4444',
    pending: '#9CA3AF',
    retrying: '#F59E0B',
  },
} as const

export { colors }

const theme = createTheme({
  palette: {
    primary: {
      main: colors.accent,
    },
    secondary: {
      main: '#6B7280',
      light: '#9CA3AF',
      dark: '#374151',
    },
    error: {
      main: '#EF4444',
    },
    warning: {
      main: '#F59E0B',
    },
    success: {
      main: '#10B981',
    },
    text: {
      primary: colors.text.primary,
      secondary: colors.text.secondary,
    },
    background: {
      default: colors.surface.secondary,
      paper: colors.surface.primary,
    },
    divider: colors.border.default,
  },
  typography: {
    fontFamily: "'Inter', 'Noto Sans TC', sans-serif",
    allVariants: {
      color: colors.text.primary,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
      styleOverrides: {
        root: {
          textTransform: 'none' as const,
        },
      },
    },
    MuiCard: {
      defaultProps: {
        variant: 'outlined',
      },
    },
    MuiChip: {
      defaultProps: {
        size: 'small',
      },
    },
  },
})

export default theme
