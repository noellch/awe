# AWE — Agent Workflow Engine Design Document

> Date: 2026-03-11
> Status: Approved

## 1. Positioning

AWE 是一個 **deterministic workflow engine for LLM agent orchestration**。核心洞察：K8s 的假設（stateless、replaceable nodes）不適用於 LLM agents，因此我們不複製 K8s，而是建立一個專為 agent 特性設計的 workflow engine。

### 與 Temporal/Airflow 的差異

LLM agent 有三個 Temporal 未覆蓋的 gap：

1. **Semantic Context** — Agent 之間需要語義級別的上下文傳遞，不只是資料管道
2. **Non-binary Quality** — Agent 輸出品質不是 pass/fail，需要多層驗證
3. **Dynamic Capabilities** — Agent 能力是動態的，dispatch 需要智慧匹配

## 2. Core Architecture

```
┌─────────────────────────────────────────────┐
│              Pipeline Runtime               │
│  (Deterministic orchestration — pure code)  │
├─────────┬───────────┬───────────┬──────────┤
│ Context │  Quality  │ Agent     │ Config   │
│ Bus     │  Gate     │ Registry  │ Loader   │
├─────────┴───────────┴───────────┴──────────┤
│              Agent Runtime                  │
│  (Pluggable: Direct API / Claude Code / …) │
├─────────────────────────────────────────────┤
│     Persistence (SQLite + Filesystem)       │
└─────────────────────────────────────────────┘
```

**關鍵原則：** Orchestration layer 是 deterministic code（不是 LLM），只有 agent execution 才用 LLM。

## 3. Pipeline YAML Syntax

```yaml
name: analyze-and-fix
description: Analyze a bug and generate a fix
context:
  repo: my-project
  language: python

steps:
  - id: analyze
    agent: researcher
    prompt: |
      Analyze the following problem: {{input.problem}}
      Identify root cause and suggest a fix approach.

  - id: fix
    agent: coder
    prompt: |
      Based on the analysis, write the code fix.
    context_from:
      - step: analyze
        compress: summary
    quality_gate:
      mode: auto
      checks:
        - type: test_runner
          command: "pytest tests/ -x"
    retry:
      max_retries: 2
      inject_failure_reason: true
```

## 4. Agent Registry

Agent 以 YAML 定義，包含：

```yaml
name: researcher
role: Senior Bug Analyst
description: Analyzes code issues and identifies root causes
model:
  provider: anthropic
  id: claude-sonnet-4-6
  max_tokens: 4096
capabilities:
  tags: [analysis, code:read, debugging]
  strengths: ["Root cause analysis", "Code pattern recognition"]
  limitations: ["Cannot execute code"]
system_prompt: |
  You are a senior software engineer specializing in debugging...
constraints:
  max_context_tokens: 32000
  max_cost_per_task: 1.0
  timeout_seconds: 300
output_schema:  # Optional — enables constrained decoding
  type: object
  properties:
    root_cause:
      type: string
    suggested_fix:
      type: string
  required: [root_cause, suggested_fix]
```

## 5. Context Bus

管理 agent 之間的上下文流動：

- **Compression Strategies**: `full`（原文）、`summary`（用 Haiku 摘要）、`diff_only`（只抽取 code blocks 和 diffs）
- **Caching**: 壓縮結果會 cache，避免重複壓縮
- **Prompt Assembly**: 自動組裝 pipeline context + upstream context + failure reason + task prompt

## 6. Quality Gate

三階段驗證：

### Phase 1: Format Check（Deterministic, Zero Cost）
- 空輸出檢查
- 過長輸出檢查（>200K chars）
- Schema validation（required fields + type checking）

### Phase 2: Content Check（Based on Mode）

| Mode | 行為 |
|------|------|
| `auto` | 執行 shell commands（test_runner, linter） |
| `agent` | 用另一個 LLM（Haiku）review 輸出，回傳 structured verdict |
| `human` | 未來：需要人工審核 |

### Agent Review Verdict Schema
```json
{
  "approved": true/false,
  "issues": ["issue 1", "issue 2"],
  "summary": "Brief review summary"
}
```

**Error handling**: 如果 reviewer agent 本身出錯，gate passes through（不阻塞 pipeline）。

## 7. Dispatcher（Phase 3+）

Task-to-agent matching：Filter → Rank → Select

- **Filter**: 依 capability tags 篩選合格 agents
- **Rank**: 依 strengths 和歷史表現排序
- **Select**: 選最佳 agent，支援 exploration rate（偶爾嘗試非最佳 agent）

> 目前 MVP 階段，agent 在 pipeline YAML 中直接指定，dispatcher 延後實作。

## 8. Agent Runtime

Pluggable interface（Protocol）：

```python
class AgentRuntime(Protocol):
    async def execute(self, agent, task, context) -> TaskOutput: ...
```

目前實作 `DirectAPIRuntime`：直接呼叫 Anthropic API。

支援兩種模式：
- **Plain**: 標準文字完成
- **Structured**: 使用 Anthropic `output_format` constrained decoding，保證 JSON schema compliance

## 9. Persistence

- **SQLite（WAL mode）**: pipeline_runs、step_runs、events 三張表
- **Filesystem**: `{runs_dir}/{run_id}/{step_id}/` 存放 raw output、structured output、compressed versions

## 10. Technical Decisions

| 決策 | 選擇 | 原因 |
|------|------|------|
| Language | Python | Anthropic SDK 生態系最完整 |
| Framework | 無（lightweight custom） | 避免 Temporal/Celery 的過度抽象 |
| Storage | SQLite + Filesystem | 零依賴部署，WAL 支援並發讀取 |
| Embedding | 不使用 | MVP 不需要向量搜尋 |
| Runtime | Abstract interface | 未來可接 Claude Code、其他 LLM |
| Monitoring | SQLite events + CLI | MVP 夠用，未來加 Web UI |
| UI | CLI + Web UI | CLI 給開發者，Web UI 是產品核心 |

## 11. Roadmap

### Phase 1: Foundation（已完成）
- Data models（Pipeline, Agent, Task）
- Config loader（YAML → Pydantic）
- SQLite persistence
- Filesystem raw store
- Context Bus with compression
- Quality Gate（format + auto + agent modes）
- Agent Runtime（Direct API）
- Pipeline Runtime（sequential execution + retry）
- CLI（run, status, list）

### Phase 2: API + UI Foundation（進行中）
- FastAPI REST API
- SSE real-time streaming
- React frontend skeleton
- MUI theme + TanStack Router
- Custom icon system

### Phase 3: Visual Operation Center
- Canvas editor（@xyflow/react）
- Pipeline designer（drag & drop nodes）
- Real-time execution monitoring
- Agent management UI

### Phase 4: Advanced Features
- Dispatcher（intelligent agent matching）
- Parallel step execution
- Human-in-the-loop quality gate
- Plugin system for custom runtimes
- Team collaboration features

## 12. Open Questions (Resolved)

| 問題 | 決定 |
|------|------|
| 要不要用 Temporal? | 不要，lightweight custom |
| 前端語言？ | TypeScript（React + Vite） |
| 雙語言管理？ | OpenAPI auto-gen + JSON Schema as shared contract |
| 要 embedding/RAG? | MVP 不需要 |
| Real-time 機制？ | SSE（不是 WebSocket） |
| UI 框架？ | MUI（不是 Tailwind） |
| Canvas library? | @xyflow/react |
| State management? | Nano Stores |
