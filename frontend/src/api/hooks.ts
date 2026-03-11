import { useQuery } from '@tanstack/react-query'
import { fetchApi } from './client'

interface Pipeline {
  id: string
  name: string
  status: string
}

interface Agent {
  id: string
  name: string
  type: string
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
    queryFn: () => fetchApi<Pipeline[]>('/api/pipelines'),
  })
}

export function useAgents() {
  return useQuery({
    queryKey: ['agents'],
    queryFn: () => fetchApi<Agent[]>('/api/agents'),
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
