"""Tests for YAML config loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from awe.config.loader import load_agent, load_pipeline


EXAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "examples"


def test_load_pipeline():
    path = EXAMPLES_DIR / "pipelines" / "analyze-and-fix.yaml"
    pipeline = load_pipeline(path)
    assert pipeline.name == "analyze-and-fix"
    assert len(pipeline.steps) == 2
    assert pipeline.steps[0].id == "analyze"
    assert pipeline.steps[1].id == "fix"
    assert pipeline.steps[1].context_from[0].step == "analyze"
    assert pipeline.steps[1].context_from[0].compress == "summary"


def test_load_agent_researcher():
    path = EXAMPLES_DIR / "agents" / "researcher.yaml"
    agent = load_agent(path)
    assert agent.name == "researcher"
    assert agent.model.id == "claude-sonnet-4-6"
    assert "analysis" in agent.capabilities.tags
    assert agent.system_prompt


def test_load_agent_coder():
    path = EXAMPLES_DIR / "agents" / "coder.yaml"
    agent = load_agent(path)
    assert agent.name == "coder"
    assert agent.model.max_tokens == 8192
    assert "code:write" in agent.capabilities.tags
