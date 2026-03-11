"""Pipeline and Step data models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ContextFrom(BaseModel):
    """Defines how to pull context from an upstream step."""

    step: str
    compress: str = "full"  # full, summary, diff_only


class QualityGateCheck(BaseModel):
    """A single quality gate check configuration."""

    type: str  # schema, assertion, test_runner, linter
    command: str | None = None
    expr: str | None = None
    schema_name: str | None = Field(None, alias="schema")


class QualityGateConfig(BaseModel):
    """Quality gate configuration for a step."""

    mode: str = "auto"  # auto, agent, human
    checks: list[QualityGateCheck] = Field(default_factory=list)
    reviewer: str | None = None
    review_prompt: str | None = None

    model_config = {"populate_by_name": True}


class RetryStrategy(BaseModel):
    """Retry strategy for a step."""

    max_retries: int = 2
    inject_failure_reason: bool = True


class Step(BaseModel):
    """A single step in a pipeline."""

    id: str
    agent: str
    prompt: str
    context_from: list[ContextFrom] = Field(default_factory=list)
    quality_gate: QualityGateConfig | None = None
    retry: RetryStrategy = Field(default_factory=RetryStrategy)


class Pipeline(BaseModel):
    """A pipeline definition loaded from YAML."""

    name: str
    description: str = ""
    context: dict[str, str] = Field(default_factory=dict)
    steps: list[Step]

    def step_order(self) -> list[str]:
        """Return step IDs in execution order (sequential for MVP)."""
        return [step.id for step in self.steps]

    def get_step(self, step_id: str) -> Step:
        """Get a step by ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        raise ValueError(f"Step '{step_id}' not found in pipeline '{self.name}'")
