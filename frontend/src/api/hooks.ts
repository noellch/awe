import { useQuery } from '@tanstack/react-query'
import { fetchApi } from './client'

export interface PipelineSummary {
  name: string
  description: string
  step_count: number
  file_path: string
}

export interface PipelineDetail {
  name: string
  description: string
  context: Record<string, string>
  steps: Array<{ id: string; agent: string; prompt: string }>
}

export interface AgentSummary {
  name: string
  role: string | null
  model_id: string
  capabilities_tags: string[]
}

interface Run {
  id: string
  pipeline_id: string
  status: string
  started_at: string
  finished_at?: string
}

interface RunsParams {
  pipeline_id?: string
  status?: string
  limit?: number
  offset?: number
}

export function usePipelines() {
  return useQuery({
    queryKey: ['pipelines'],
    queryFn: () => fetchApi<PipelineSummary[]>('/api/pipelines'),
  })
}

export function usePipeline(name: string) {
  return useQuery({
    queryKey: ['pipeline', name],
    queryFn: () => fetchApi<PipelineDetail>(`/api/pipelines/${name}`),
    enabled: !!name,
  })
}

export function useAgents() {
  return useQuery({
    queryKey: ['agents'],
    queryFn: () => fetchApi<AgentSummary[]>('/api/agents'),
  })
}

export function useAgent(name: string) {
  return useQuery({
    queryKey: ['agent', name],
    queryFn: () => fetchApi<AgentSummary>(`/api/agents/${name}`),
    enabled: !!name,
  })
}

export function useRuns(params?: RunsParams) {
  return useQuery({
    queryKey: ['runs', params],
    queryFn: () => {
      const searchParams = new URLSearchParams()
      if (params?.pipeline_id) searchParams.set('pipeline_id', params.pipeline_id)
      if (params?.status) searchParams.set('status', params.status)
      if (params?.limit) searchParams.set('limit', String(params.limit))
      if (params?.offset) searchParams.set('offset', String(params.offset))
      const qs = searchParams.toString()
      return fetchApi<Run[]>(`/api/runs${qs ? `?${qs}` : ''}`)
    },
  })
}

export function useRun(runId: string) {
  return useQuery({
    queryKey: ['run', runId],
    queryFn: () => fetchApi<Run>(`/api/runs/${runId}`),
    enabled: !!runId,
  })
}
