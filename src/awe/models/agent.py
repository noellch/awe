"""Agent profile data models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """LLM model configuration."""

    provider: str = "anthropic"
    id: str = "claude-sonnet-4-6"
    max_tokens: int = 4096


class Capability(BaseModel):
    """Agent capability description."""

    tags: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class Constraints(BaseModel):
    """Agent resource constraints."""

    max_context_tokens: int = 32000
    max_cost_per_task: float = 1.0
    timeout_seconds: int = 300


class AgentProfile(BaseModel):
    """An agent profile loaded from YAML."""

    name: str
    role: str | None = None
    description: str = ""
    model: ModelConfig = Field(default_factory=ModelConfig)
    capabilities: Capability = Field(default_factory=Capability)
    system_prompt: str = ""
    tools: list[str] = Field(default_factory=list)
    constraints: Constraints = Field(default_factory=Constraints)
    output_schema: dict | None = None

    def effective_role(self) -> str:
        """Return the role, falling back to name."""
        return self.role or self.name
