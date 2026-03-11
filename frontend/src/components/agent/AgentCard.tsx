import Card from '@mui/material/Card'
import CardActionArea from '@mui/material/CardActionArea'
import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'
import Chip from '@mui/material/Chip'
import StatusDot from '../icons/StatusDot'
import type { AgentSummary } from '../../api/hooks'

interface AgentCardProps {
  agent: AgentSummary
  onClick: () => void
}

function getShortModel(modelId: string): string {
  // Extract short name from model_id like "claude-sonnet-4-6" -> "sonnet"
  const parts = modelId.split('-')
  // Look for known model family names
  const families = ['sonnet', 'opus', 'haiku']
  for (const family of families) {
    if (parts.includes(family)) return family
  }
  // Fallback: return the model_id as-is
  return modelId
}

export default function AgentCard({ agent, onClick }: AgentCardProps) {
  return (
    <Card
      variant="outlined"
      sx={{
        borderRadius: '8px',
        transition: 'border-color 150ms',
        '&:hover': {
          borderColor: 'primary.main',
        },
      }}
    >
      <CardActionArea
        onClick={onClick}
        sx={{ p: 2, display: 'flex', flexDirection: 'column', alignItems: 'stretch' }}
      >
        {/* Top row: StatusDot + name + model badge */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <StatusDot status="pending" size={8} />
            <Typography sx={{ fontWeight: 600 }}>{agent.name}</Typography>
          </Box>
          <Chip
            label={getShortModel(agent.model_id)}
            variant="filled"
            size="small"
            sx={{
              borderRadius: '4px',
              bgcolor: '#F3F4F6',
              fontFamily: 'monospace',
              color: 'text.secondary',
            }}
          />
        </Box>

        {/* Role */}
        {agent.role && (
          <Typography
            color="text.secondary"
            sx={{ fontSize: 14, mt: 0.5 }}
          >
            {agent.role}
          </Typography>
        )}

        {/* Capability tags */}
        {agent.capabilities_tags.length > 0 && (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1.5 }}>
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
        )}
      </CardActionArea>
    </Card>
  )
}
