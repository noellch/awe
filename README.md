# AWE - Agent Workflow Engine

A workflow engine for LLM agent orchestration. Deterministic orchestration layer coordinates agent execution through YAML-defined pipelines, with built-in context compression and quality verification.

## Quick Start

```bash
# Install
uv sync

# Run a pipeline
uv run awe run analyze-and-fix \
  --pipeline-dir examples/pipelines \
  --agent-dir examples/agents \
  --input '{"problem": "The API returns 500 when user has no email"}'

# Check status
uv run awe status

# View a specific run
uv run awe status <run-id>
```

## Architecture

```
YAML Pipeline Definition
  -> Pipeline Runtime (DAG execution, state machine)
  -> Context Bus (compress upstream output for downstream)
  -> Quality Gate (verify agent output)
  -> Agent Runtime (call LLM API)
  -> SQLite (state) + Filesystem (raw outputs)
```

## Core Concepts

- **Pipeline** - A YAML-defined sequence of steps, each assigned to an agent
- **Agent Profile** - YAML-defined agent with model config, system prompt, capabilities
- **Context Bus** - Compresses and assembles upstream outputs for downstream agents
- **Quality Gate** - Validates agent output (format check + configurable content checks)
- **Agent Runtime** - Executes agent tasks via LLM API (pluggable interface)

## Project Structure

```
src/awe/
  cli.py              # CLI entry point
  models/             # Pydantic data models
  runtime/            # Pipeline and Agent runtime
  context/            # Context Bus, Raw Store, Compressor
  quality/            # Quality Gate
  persistence/        # SQLite state management
  config/             # YAML loader
examples/
  pipelines/          # Example pipeline definitions
  agents/             # Example agent profiles
```

## Design Document

See [docs/plans/2026-03-11-agent-workflow-engine-design.md](../docs/plans/2026-03-11-agent-workflow-engine-design.md) for the full design.
