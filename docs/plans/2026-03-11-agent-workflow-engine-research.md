# AWE — Technical Research

> Date: 2026-03-11
> Status: Complete

## 1. Module Breakdown

```
src/awe/
├── models/          # Pydantic data models
│   ├── pipeline.py  # Pipeline, Step, ContextFrom, QualityGateConfig
│   ├── agent.py     # AgentProfile, ModelConfig, Capability, Constraints
│   └── task.py      # Task, TaskOutput, TaskStatus, AssembledContext
├── config/
│   └── loader.py    # YAML → Pydantic model loading
├── context/
│   ├── bus.py       # Context assembly + prompt building
│   ├── store.py     # Filesystem raw output storage
│   └── compressor.py# Compression strategies (full/summary/diff_only)
├── quality/
│   └── gate.py      # Quality gate (format + auto + agent modes)
├── runtime/
│   ├── agent_runtime.py   # AgentRuntime protocol + DirectAPIRuntime
│   └── pipeline_runtime.py# PipelineRunner (orchestration + retry)
├── persistence/
│   └── db.py        # SQLite async database
├── api/
│   ├── app.py       # FastAPI app factory
│   ├── server.py    # Uvicorn entry point
│   ├── deps.py      # Dependency injection
│   ├── schemas.py   # API response models
│   └── routers/     # REST + SSE endpoints
└── cli.py           # Click CLI
```

## 2. Data Flow

```
User (CLI/API)
  → load_pipeline(name) → Pipeline model
  → PipelineRunner.run(pipeline, input_data)
    → for each step:
      → find_agent(step.agent) → AgentProfile
      → ContextBus.assemble() → AssembledContext
        → read upstream outputs from RawStore
        → compress via Compressor (full/summary/diff_only)
        → build user_prompt with all context
      → AgentRuntime.execute(agent, task, context) → TaskOutput
        → Anthropic API call (plain or structured)
      → RawStore.save_output()
      → quality_check(output, config)
        → Phase 1: format validation
        → Phase 2: auto (shell commands) or agent (LLM review)
      → if failed + retries remaining → inject failure reason, retry
      → Database: log step_run + events
    → Database: update pipeline_run status
```

## 3. Project Setup

- **Package manager**: uv (fast Python package manager)
- **Layout**: src layout (`src/awe/`)
- **Build**: `uv_build` backend
- **Python**: >= 3.12
- **Testing**: pytest + pytest-asyncio (asyncio_mode = "auto")

## 4. Anthropic Structured Outputs

使用 `output_format` parameter 啟用 constrained decoding：

```python
response = await client.messages.create(
    model=agent.model.id,
    max_tokens=agent.model.max_tokens,
    messages=messages,
    output_format={
        "type": "json",
        "schema": agent.output_schema,
    },
)
```

保證回應符合 JSON schema，不需要 retry parsing。用於：
- Agent 有定義 `output_schema` 時的正常執行
- Quality gate agent review（固定 schema: approved/issues/summary）

## 5. SQLite Schema

```sql
CREATE TABLE pipeline_runs (
    id TEXT PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    context TEXT,        -- JSON
    input TEXT,          -- JSON
    created_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT
);

CREATE TABLE step_runs (
    id TEXT PRIMARY KEY,
    pipeline_run_id TEXT NOT NULL REFERENCES pipeline_runs(id),
    step_id TEXT NOT NULL,
    agent_name TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    attempt INTEGER DEFAULT 1,
    output_path TEXT,
    tokens_used INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0.0,
    duration_ms INTEGER DEFAULT 0,
    failure_reason TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_run_id TEXT NOT NULL REFERENCES pipeline_runs(id),
    step_id TEXT,
    event_type TEXT NOT NULL,
    payload TEXT,        -- JSON
    created_at TEXT DEFAULT (datetime('now'))
);
```

WAL mode 啟用並發讀取，適合 API server 同時讀取 + pipeline runner 同時寫入。

## 6. Filesystem Structure

```
.awe/
├── awe.db              # SQLite database
└── runs/
    └── run-20260311-143022-a1b2c3/
        ├── analyze/
        │   ├── output.txt          # Raw agent output
        │   ├── structured.json     # Parsed JSON (if applicable)
        │   └── compressed_summary.txt  # Cached compression
        └── fix/
            ├── output.txt
            └── structured.json
```

## 7. Cost Estimation

Approximate pricing per million tokens (early 2026):

| Model | Input | Output |
|-------|-------|--------|
| claude-opus-4-6 | $15.0 | $75.0 |
| claude-sonnet-4-6 | $3.0 | $15.0 |
| claude-haiku-4-5 | $0.80 | $4.0 |

Quality gate agent review 使用 Haiku 以降低成本。Summary compression 也使用 Haiku。

## 8. Existing Framework Analysis

| Framework | 適合度 | 原因 |
|-----------|--------|------|
| Temporal | 中 | 強大但過度複雜，缺少 semantic context 概念 |
| Airflow | 低 | 設計給 data pipeline，不適合 interactive agent |
| LangGraph | 中 | 太 LLM-centric，orchestration 也靠 LLM |
| CrewAI | 中 | 角色概念好但缺少 deterministic control |

結論：Lightweight custom 最合適，避免框架限制，保持架構簡潔。
