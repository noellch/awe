import Drawer from '@mui/material/Drawer'
import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'
import Chip from '@mui/material/Chip'
import Divider from '@mui/material/Divider'
import Button from '@mui/material/Button'
import type { AgentSummary } from '../../api/hooks'

interface AgentDrawerProps {
  open: boolean
  agent: AgentSummary | null
  onClose: () => void
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <Box sx={{ display: 'flex', py: 0.75 }}>
      <Typography
        variant="body2"
        color="text.secondary"
        sx={{ width: 120, flexShrink: 0 }}
      >
        {label}
      </Typography>
      <Typography variant="body2">{value}</Typography>
    </Box>
  )
}

export default function AgentDrawer({ open, agent, onClose }: AgentDrawerProps) {
  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      PaperProps={{ sx: { width: 480 } }}
    >
      {agent && (
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          {/* Content area */}
          <Box sx={{ flex: 1, overflow: 'auto', p: 3 }}>
            {/* Profile section */}
            <Typography variant="h5" sx={{ fontWeight: 600 }}>
              {agent.name}
            </Typography>
            <Box sx={{ mt: 2 }}>
              <DetailRow label="Name" value={agent.name} />
              <DetailRow label="Role" value={agent.role ?? '-'} />
              <DetailRow label="Model" value={agent.model_id} />
            </Box>

            <Divider sx={{ my: 3 }} />

            {/* Capabilities section */}
            <Typography variant="subtitle2" sx={{ mb: 1.5 }}>
              Capabilities
            </Typography>
            {agent.capabilities_tags.length > 0 ? (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {agent.capabilities_tags.map((tag) => (
                  <Chip
                    key={tag}
                    label={tag}
                    variant="outlined"
                    size="small"
                    sx={{ borderRadius: '4px' }}
                  />
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                No capabilities defined
              </Typography>
            )}

            <Divider sx={{ my: 3 }} />

            {/* History section */}
            <Typography variant="subtitle2" sx={{ mb: 1.5 }}>
              History
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Coming soon
            </Typography>
          </Box>

          {/* Fixed bottom action bar */}
          <Box
            sx={{
              p: 2,
              borderTop: 1,
              borderColor: 'divider',
              display: 'flex',
              gap: 1,
              justifyContent: 'flex-end',
            }}
          >
            <Button variant="outlined" disabled>
              Edit YAML
            </Button>
            <Button variant="outlined" color="error" disabled>
              Delete
            </Button>
          </Box>
        </Box>
      )}
    </Drawer>
  )
}
