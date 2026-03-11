"""Tests for agent-mode Quality Gate (using mocks)."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from awe.models.pipeline import QualityGateConfig
from awe.models.task import TaskOutput
from awe.quality.gate import check, _build_review_prompt


def test_build_review_prompt_default():
    """Review prompt includes the output."""
    output = TaskOutput(raw_text="Here is my analysis of the bug.")
    prompt = _build_review_prompt(output)
    assert "quality reviewer" in prompt.lower()
    assert "Here is my analysis" in prompt


def test_build_review_prompt_custom():
    """Review prompt includes custom criteria."""
    output = TaskOutput(raw_text="Some code output.")
    prompt = _build_review_prompt(output, custom_prompt="Check for security issues")
    assert "Check for security issues" in prompt
    assert "Some code output." in prompt


@pytest.mark.asyncio
async def test_agent_review_approved():
    """Agent review passes when reviewer approves."""
    output = TaskOutput(raw_text="Good output here.")
    config = QualityGateConfig(mode="agent", reviewer="code-reviewer")

    # Mock the Anthropic API response
    mock_response = MagicMock()
    mock_text_block = MagicMock()
    mock_text_block.type = "text"
    mock_text_block.text = json.dumps({
        "approved": True,
        "issues": [],
        "summary": "Output looks good",
    })
    mock_response.content = [mock_text_block]

    with patch("awe.quality.gate.anthropic.AsyncAnthropic") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        result = await check(output, config)
        assert result.passed
        assert result.phase == "agent_review"


@pytest.mark.asyncio
async def test_agent_review_rejected():
    """Agent review fails when reviewer finds issues."""
    output = TaskOutput(raw_text="Bad output here.")
    config = QualityGateConfig(mode="agent", reviewer="code-reviewer")

    mock_response = MagicMock()
    mock_text_block = MagicMock()
    mock_text_block.type = "text"
    mock_text_block.text = json.dumps({
        "approved": False,
        "issues": ["Missing error handling", "Incomplete solution"],
        "summary": "Output needs improvement",
    })
    mock_response.content = [mock_text_block]

    with patch("awe.quality.gate.anthropic.AsyncAnthropic") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        result = await check(output, config)
        assert not result.passed
        assert "Missing error handling" in result.reason
        assert result.phase == "agent_review"


@pytest.mark.asyncio
async def test_agent_review_error_passes_through():
    """If the review agent errors, the gate passes with a warning."""
    output = TaskOutput(raw_text="Some output.")
    config = QualityGateConfig(mode="agent", reviewer="code-reviewer")

    with patch("awe.quality.gate.anthropic.AsyncAnthropic") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(side_effect=Exception("API down"))
        mock_client_cls.return_value = mock_client

        result = await check(output, config)
        # Should pass through on error (don't block the pipeline)
        assert result.passed
        assert "skipped" in result.reason.lower()


@pytest.mark.asyncio
async def test_agent_review_with_custom_prompt():
    """Agent review uses custom review_prompt from config."""
    output = TaskOutput(raw_text="Code output.")
    config = QualityGateConfig(
        mode="agent",
        reviewer="code-reviewer",
        review_prompt="Check for SQL injection vulnerabilities",
    )

    mock_response = MagicMock()
    mock_text_block = MagicMock()
    mock_text_block.type = "text"
    mock_text_block.text = json.dumps({
        "approved": True,
        "issues": [],
        "summary": "No SQL injection found",
    })
    mock_response.content = [mock_text_block]

    with patch("awe.quality.gate.anthropic.AsyncAnthropic") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client

        result = await check(output, config)
        assert result.passed

        # Verify the custom prompt was included in the API call
        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs["messages"]
        assert "SQL injection" in messages[0]["content"]
