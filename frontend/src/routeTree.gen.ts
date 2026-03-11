import { createRouter } from '@tanstack/react-router'
import { Route as rootRoute } from './routes/__root'
import { Route as IndexRoute } from './routes/index'
import { Route as PipelinesRoute } from './routes/pipelines'
import { Route as PipelineCanvasRoute } from './routes/pipelines.$pipelineId'
import { Route as RunsRoute } from './routes/runs'
import { Route as AgentsRoute } from './routes/agents'
import { Route as SettingsRoute } from './routes/settings'

const routeTree = rootRoute.addChildren([
  IndexRoute,
  PipelinesRoute,
  PipelineCanvasRoute,
  RunsRoute,
  AgentsRoute,
  SettingsRoute,
])

export const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
