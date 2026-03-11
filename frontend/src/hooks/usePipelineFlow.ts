import { useMemo, useEffect } from 'react'
import { useNodesState, useEdgesState, type Edge } from '@xyflow/react'
import type { StepNodeType } from '../components/canvas/StepNode'

interface PipelineDetail {
  name: string
  description: string
  context: Record<string, string>
  steps: Array<{ id: string; agent: string; prompt: string }>
}

export default function usePipelineFlow(pipeline: PipelineDetail | undefined) {
  const initialNodes = useMemo<StepNodeType[]>(() => {
    if (!pipeline) return []
    return pipeline.steps.map((step, index) => ({
      id: step.id,
      type: 'step' as const,
      position: { x: index * 250, y: 100 },
      data: {
        label: step.id,
        agent: step.agent,
        status: 'pending' as const,
        prompt: step.prompt,
      },
    }))
  }, [pipeline])

  const initialEdges = useMemo<Edge[]>(() => {
    if (!pipeline) return []
    return pipeline.steps.slice(0, -1).map((step, index) => ({
      id: `e-${step.id}-${pipeline.steps[index + 1].id}`,
      source: step.id,
      target: pipeline.steps[index + 1].id,
      type: 'smoothstep',
      animated: false,
      style: { stroke: '#E5E7EB', strokeWidth: 1.5 },
    }))
  }, [pipeline])

  const [nodes, setNodes, onNodesChange] = useNodesState<StepNodeType>(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  useEffect(() => {
    setNodes(initialNodes)
  }, [initialNodes, setNodes])

  useEffect(() => {
    setEdges(initialEdges)
  }, [initialEdges, setEdges])

  return { nodes, edges, onNodesChange, onEdgesChange }
}
