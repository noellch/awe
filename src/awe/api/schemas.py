"""API response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class PipelineSummary(BaseModel):
    name: str
    description: str = ""
    step_count: int
    file_path: str


class PipelineDetail(BaseModel):
    name: str
    description: str = ""
    context: dict[str, str] = {}
    steps: list[StepInfo]


class StepInfo(BaseModel):
    id: str
    agent: str
    prompt: str


class RunSummary(BaseModel):
    id: str
    pipeline_name: str
    status: str
    created_at: str | None = None
    completed_at: str | None = None


class RunDetail(RunSummary):
    step_runs: list[StepRunInfo] = []


class StepRunInfo(BaseModel):
    step_id: str
    agent_name: str | None = None
    status: str
    attempt: int = 1
    tokens_used: int = 0
    cost_usd: float = 0.0
    duration_ms: int = 0
    failure_reason: str | None = None


class AgentSummary(BaseModel):
    name: str
    role: str | None = None
    model_id: str = ""
    capabilities_tags: list[str] = []


class RunCreateResponse(BaseModel):
    run_id: str


class SSEEvent(BaseModel):
    event_type: str
    step_id: str | None = None
    payload: dict[str, Any] = {}
    created_at: str | None = None


# Rebuild forward references
PipelineDetail.model_rebuild()
