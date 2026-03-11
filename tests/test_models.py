"""Tests for data models."""

from __future__ import annotations

from awe.models.agent import AgentProfile, ModelConfig
from awe.models.pipeline import ContextFrom, Pipeline, QualityGateConfig, Step
from awe.models.task import AssembledContext, TaskOutput, TaskStatus, UpstreamContext


def test_pipeline_model():
    pipeline = Pipeline(
        name="test-pipeline",
        description="A test pipeline",
        context={"repo": "rubato"},
        steps=[
            Step(
                id="analyze",
                agent="researcher",
                prompt="Analyze this: {{input.problem}}",
            ),
            Step(
                id="fix",
                agent="coder",
                prompt="Fix it",
                context_from=[ContextFrom(step="analyze", compress="summary")],
            ),
        ],
    )
    assert pipeline.name == "test-pipeline"
    assert pipeline.step_order() == ["analyze", "fix"]
    assert pipeline.get_step("analyze").agent == "researcher"
    assert pipeline.get_step("fix").context_from[0].compress == "summary"


def test_agent_profile_model():
    agent = AgentProfile(
        name="test-agent",
        model=ModelConfig(id="claude-sonnet-4-6", max_tokens=4096),
        system_prompt="You are a test agent.",
    )
    assert agent.effective_role() == "test-agent"
    assert agent.model.id == "claude-sonnet-4-6"

    agent_with_role = AgentProfile(name="coder-v2", role="coder")
    assert agent_with_role.effective_role() == "coder"


def test_task_output_model():
    output = TaskOutput(
        raw_text="Hello, world!",
        tokens_used=100,
        cost_usd=0.001,
        duration_ms=500,
    )
    assert output.raw_text == "Hello, world!"
    assert output.structured is None


def test_task_status_enum():
    assert TaskStatus.PENDING == "pending"
    assert TaskStatus.PASSED == "passed"
    assert TaskStatus.FAILED == "failed"


def test_assembled_context():
    ctx = AssembledContext(
        system_prompt="You are helpful.",
        user_prompt="Do the thing.",
        upstream_context=[
            UpstreamContext(
                step_id="analyze",
                compress_strategy="summary",
                content="Summary of analysis",
            )
        ],
    )
    assert len(ctx.upstream_context) == 1
    assert ctx.upstream_context[0].step_id == "analyze"


def test_quality_gate_config():
    config = QualityGateConfig(mode="auto")
    assert config.mode == "auto"
    assert config.checks == []
    assert config.reviewer is None
