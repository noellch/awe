import { useState, useMemo, useCallback, type MouseEvent as ReactMouseEvent } from 'react'
import { createRoute } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import {
  ReactFlow,
  Background,
  BackgroundVariant,
  Controls,
  type NodeTypes,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'
import { Route as rootRoute } from './__root'
import { fetchApi } from '../api/client'
import usePipelineFlow from '../hooks/usePipelineFlow'
import StepNode from '../components/canvas/StepNode'
import type { StepNodeType } from '../components/canvas/StepNode'
import CanvasToolbar from '../components/canvas/CanvasToolbar'
import NodeConfigPanel from '../components/canvas/NodeConfigPanel'

interface PipelineDetail {
  name: string
  description: string
  context: Record<string, string>
  steps: Array<{ id: string; agent: string; prompt: string }>
}

export const Route = createRoute({
  getParentRoute: () => rootRoute,
  path: '/pipelines/$pipelineId',
  component: CanvasPage,
})

const nodeTypes: NodeTypes = { step: StepNode }

function CanvasPage() {
  const { pipelineId } = Route.useParams()

  const { data: pipeline, isLoading } = useQuery({
    queryKey: ['pipeline', pipelineId],
    queryFn: () => fetchApi<PipelineDetail>(`/api/pipelines/${pipelineId}`),
  })

  const { nodes, edges, onNodesChange, onEdgesChange } = usePipelineFlow(pipeline)

  const [selectedNode, setSelectedNode] = useState<StepNodeType | null>(null)

  const handleNodeClick = useCallback(
    (_event: ReactMouseEvent, node: StepNodeType) => {
      setSelectedNode(node)
    },
    [],
  )

  const handlePaneClick = useCallback(() => {
    setSelectedNode(null)
  }, [])

  const handlePanelClose = useCallback(() => {
    setSelectedNode(null)
  }, [])

  // Keep selectedNode data in sync with nodes state
  const currentSelectedNode = useMemo(() => {
    if (!selectedNode) return null
    return nodes.find((n) => n.id === selectedNode.id) ?? null
  }, [selectedNode, nodes])

  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: 'calc(100vh - 48px)',
          flex: 1,
          m: -3,
        }}
      >
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1, m: -3, height: 'calc(100vh - 48px)' }}>
      <CanvasToolbar pipelineName={pipeline?.name ?? pipelineId} />
      <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <Box sx={{ flex: 1, position: 'relative' }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={handleNodeClick}
            onPaneClick={handlePaneClick}
            nodeTypes={nodeTypes}
            fitView
          >
            <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#E5E7EB" />
            <Controls />
          </ReactFlow>
        </Box>
        <NodeConfigPanel
          selectedNode={currentSelectedNode}
          onClose={handlePanelClose}
        />
      </Box>
    </Box>
  )
}
