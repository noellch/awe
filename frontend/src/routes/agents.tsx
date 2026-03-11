import { useState, useMemo } from 'react'
import { createRoute } from '@tanstack/react-router'
import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'
import TextField from '@mui/material/TextField'
import Button from '@mui/material/Button'
import Grid from '@mui/material/Grid'
import Skeleton from '@mui/material/Skeleton'
import Card from '@mui/material/Card'
import { Route as rootRoute } from './__root'
import { useAgents } from '../api/hooks'
import type { AgentSummary } from '../api/hooks'
import AgentCard from '../components/agent/AgentCard'
import AgentDrawer from '../components/agent/AgentDrawer'

export const Route = createRoute({
  getParentRoute: () => rootRoute,
  path: '/agents',
  component: AgentsPage,
})

function AgentsPage() {
  const { data: agents, isLoading } = useAgents()
  const [search, setSearch] = useState('')
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<AgentSummary | null>(null)

  const filtered = useMemo(() => {
    if (!agents) return []
    if (!search.trim()) return agents
    const q = search.trim().toLowerCase()
    return agents.filter((a) => a.name.toLowerCase().includes(q))
  }, [agents, search])

  const handleCardClick = (agent: AgentSummary) => {
    setSelectedAgent(agent)
    setDrawerOpen(true)
  }

  return (
    <Box>
      {/* Top action bar */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          mb: 3,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
          <Typography variant="h4">Agents</Typography>
          {agents && (
            <Typography variant="body2" color="text.secondary">
              ({agents.length})
            </Typography>
          )}
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <TextField
            size="small"
            placeholder="Search agents..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            sx={{ width: 240 }}
          />
          <Button variant="text" disabled>
            + New Agent
          </Button>
        </Box>
      </Box>

      {/* Loading state */}
      {isLoading && (
        <Grid container spacing={3}>
          {[0, 1, 2].map((i) => (
            <Grid size={{ xs: 12, md: 4, xl: 3 }} key={i}>
              <Card variant="outlined" sx={{ borderRadius: '8px', p: 2 }}>
                <Skeleton variant="text" width="60%" height={28} />
                <Skeleton variant="text" width="80%" height={20} sx={{ mt: 0.5 }} />
                <Box sx={{ display: 'flex', gap: 0.5, mt: 1.5 }}>
                  <Skeleton variant="rounded" width={48} height={24} sx={{ borderRadius: '4px' }} />
                  <Skeleton variant="rounded" width={56} height={24} sx={{ borderRadius: '4px' }} />
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Data state */}
      {!isLoading && filtered.length > 0 && (
        <Grid container spacing={3}>
          {filtered.map((agent) => (
            <Grid size={{ xs: 12, md: 4, xl: 3 }} key={agent.name}>
              <AgentCard agent={agent} onClick={() => handleCardClick(agent)} />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Empty state */}
      {!isLoading && agents && filtered.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography color="text.secondary">
            {search.trim() ? 'No matching agents found' : 'No registered agents yet'}
          </Typography>
        </Box>
      )}

      {/* Agent detail drawer */}
      <AgentDrawer
        open={drawerOpen}
        agent={selectedAgent}
        onClose={() => setDrawerOpen(false)}
      />
    </Box>
  )
}
