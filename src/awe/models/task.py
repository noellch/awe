"""Task and execution data models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Status of a task/step execution."""

    PENDING = "pending"
    RUNNING = "running"
    QUALITY_CHECK = "quality_check"
    PASSED = "passed"
    FAILED = "failed"
    RETRYING = "retrying"
    ABORTED = "aborted"


class AssembledContext(BaseModel):
    """Context assembled by the Context Bus for agent execution."""

    system_prompt: str
    user_prompt: str
    pipeline_context: dict[str, str] = Field(default_factory=dict)
    upstream_context: list[UpstreamContext] = Field(default_factory=list)


class UpstreamContext(BaseModel):
    """Compressed context from an upstream step."""

    step_id: str
    compress_strategy: str
    content: str


class TaskOutput(BaseModel):
    """Output from an agent execution."""

    raw_text: str
    structured: dict | None = None
    tokens_used: int = 0
    cost_usd: float = 0.0
    duration_ms: int = 0
    model_id: str = ""


class Task(BaseModel):
    """A concrete task to execute, derived from a pipeline step."""

    step_id: str
    pipeline_run_id: str
    agent_name: str
    prompt: str
    attempt: int = 1
    failure_reason: str | None = None


# Fix forward reference
AssembledContext.model_rebuild()
