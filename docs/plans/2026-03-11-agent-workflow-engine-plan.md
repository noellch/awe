# AWE — Implementation Plan

> Date: 2026-03-11
> Status: Tasks 1-7 Complete, 8-10 In Progress

## Task Overview

| # | Task | Status | Depends On |
|---|------|--------|------------|
| 1 | Data Models | Done | none |
| 2 | Config Loader | Done | 1 |
| 3 | SQLite Persistence | Done | 1 |
| 4 | Filesystem Raw Store | Done | 1 |
| 5 | Context Bus + Compressor | Done | 2, 4 |
| 6 | Quality Gate | Done | 1 |
| 7 | Agent Runtime + Pipeline Runtime | Done | 1-6 |
| 8 | CLI | Done | 7 |
| 9 | FastAPI API Layer | Done | 7 |
| 10 | React Frontend Skeleton | Done | 9 |

## Task 1: Data Models
- **Files:** `src/awe/models/pipeline.py`, `agent.py`, `task.py`
- **Approach:** Pydantic BaseModel with type hints, enums for status
- **Acceptance criteria:** All models instantiable, serializable, with correct defaults

## Task 2: Config Loader
- **Files:** `src/awe/config/loader.py`
- **Approach:** YAML → dict → Pydantic model, search multiple directories
- **Acceptance criteria:** Load example YAMLs, raise clear errors for missing files

## Task 3: SQLite Persistence
- **Files:** `src/awe/persistence/db.py`
- **Approach:** aiosqlite with WAL mode, schema auto-creation
- **Acceptance criteria:** CRUD for pipeline_runs, step_runs, events; concurrent reads work

## Task 4: Filesystem Raw Store
- **Files:** `src/awe/context/store.py`
- **Approach:** Simple file I/O with structured directory layout
- **Acceptance criteria:** Save/read output, structured, compressed files by run_id + step_id

## Task 5: Context Bus + Compressor
- **Files:** `src/awe/context/bus.py`, `compressor.py`
- **Approach:** Strategy pattern for compression, bus assembles all context sources
- **Depends on:** 2 (loader for pipeline model), 4 (store for reading upstream)
- **Acceptance criteria:** Assemble context with upstream compression, cache compressed results

## Task 6: Quality Gate
- **Files:** `src/awe/quality/gate.py`
- **Approach:** Phase 1 (format) always runs, Phase 2 routes by mode (auto/agent)
- **Acceptance criteria:** Format validation, shell command checks, agent review with structured verdict

## Task 7: Agent Runtime + Pipeline Runtime
- **Files:** `src/awe/runtime/agent_runtime.py`, `pipeline_runtime.py`
- **Approach:** Protocol for runtime abstraction, DirectAPIRuntime for Anthropic, PipelineRunner orchestrates
- **Depends on:** 1-6 (all preceding modules)
- **Acceptance criteria:** Execute pipeline end-to-end, retry on quality gate failure, cost tracking

## Task 8: CLI
- **Files:** `src/awe/cli.py`
- **Approach:** Click with Rich formatting, commands: run, status, list
- **Depends on:** 7
- **Acceptance criteria:** `awe run`, `awe status`, `awe list` all functional with formatted output

## Task 9: FastAPI API Layer
- **Files:** `src/awe/api/` (app, server, deps, schemas, routers/)
- **Approach:** App factory pattern, CORS, lifespan DB management, SSE streaming
- **Depends on:** 7
- **Acceptance criteria:** REST endpoints for pipelines/runs/agents, SSE for real-time updates, 8 API tests passing

## Task 10: React Frontend Skeleton
- **Files:** `frontend/` (new directory)
- **Approach:** Vite + React + TypeScript, MUI theme, TanStack Router, custom icon system
- **Depends on:** 9 (API endpoints to connect to)
- **Acceptance criteria:** Build passes, routes work, TopNav with tab navigation, icon components render
