# AWE - Agent Workflow Engine

A deterministic workflow engine for LLM agent orchestration with a visual operation center. YAML-defined pipelines coordinate agent execution with built-in context compression, quality verification, and real-time monitoring.

## Project Structure

```
awe/
├── backend/            # Python: Engine + FastAPI API + CLI
│   ├── src/awe/        # Core engine
│   │   ├── api/        # FastAPI REST + SSE endpoints
│   │   ├── models/     # Pydantic data models
│   │   ├── runtime/    # Pipeline & Agent runtime
│   │   ├── context/    # Context Bus, Store, Compressor
│   │   ├── quality/    # Quality Gate
│   │   ├── persistence/# SQLite state management
│   │   ├── config/     # YAML loader
│   │   └── cli.py      # CLI entry point
│   └── tests/          # 44 tests
├── frontend/           # TypeScript: React visual operation center
│   └── src/
│       ├── components/ # UI components (icons, layout)
│       ├── routes/     # TanStack Router pages
│       ├── api/        # API client + TanStack Query hooks
│       └── theme/      # MUI theme (Linear + Notion inspired)
├── examples/           # Pipeline & Agent YAML definitions
├── schemas/            # Shared JSON Schema (planned)
├── docs/plans/         # Design documents
└── Makefile            # Unified dev commands
```

## Quick Start

### Backend

```bash
cd backend
uv sync

# Start API server (http://localhost:8000)
uv run awe-server

# Or use CLI directly
uv run awe run analyze-and-fix \
  --pipeline-dir ../examples/pipelines \
  --agent-dir ../examples/agents \
  --input '{"problem": "The API returns 500 when user has no email"}'

# Check status
uv run awe status
```

### Frontend

```bash
cd frontend
npm install

# Start dev server (http://localhost:3000)
npm run dev -- --port 3000
```

### Both (via Makefile)

```bash
make dev          # Start both backend + frontend
make test         # Run all tests
make build        # Build frontend for production
```

## Architecture

```
YAML Pipeline Definition
  -> Pipeline Runtime (sequential execution, retry logic)
  -> Context Bus (compress upstream output for downstream)
  -> Quality Gate (format check + agent review)
  -> Agent Runtime (call Anthropic API)
  -> SQLite (state) + Filesystem (raw outputs)
  -> FastAPI (REST + SSE) -> React UI (real-time canvas)
```

## Core Concepts

- **Pipeline** — YAML-defined sequence of steps, each assigned to an agent
- **Agent Profile** — YAML-defined agent with model config, system prompt, capabilities
- **Context Bus** — Compresses and routes upstream outputs to downstream agents
- **Quality Gate** — Validates agent output (format + auto/agent review modes)
- **Agent Runtime** — Executes tasks via Anthropic API (pluggable interface)

## Tech Stack

| Layer | Stack |
|-------|-------|
| Engine | Python 3.12, Pydantic, aiosqlite |
| API | FastAPI, SSE (sse-starlette) |
| CLI | Click, Rich |
| Frontend | React, TypeScript, Vite, MUI |
| Canvas | @xyflow/react |
| Routing | TanStack Router |
| Data | TanStack Query, Nano Stores |

## API Endpoints

```
GET    /api/pipelines              # List pipelines
GET    /api/pipelines/{name}       # Get pipeline detail
POST   /api/pipelines/{name}/run   # Execute pipeline

GET    /api/runs                   # List runs
GET    /api/runs/{run_id}          # Run detail with steps
GET    /api/runs/{run_id}/stream   # SSE real-time stream

GET    /api/agents                 # List agents
GET    /api/agents/{name}          # Get agent detail
```

## Design Documents

- [Architecture Design](docs/plans/2026-03-11-agent-workflow-engine-design.md)
- [Technical Research](docs/plans/2026-03-11-agent-workflow-engine-research.md)
- [Implementation Plan](docs/plans/2026-03-11-agent-workflow-engine-plan.md)
- [UI Design](docs/plans/2026-03-11-awe-ui-design.md)

## License

MIT
