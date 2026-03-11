"""Tests for Quality Gate."""

from __future__ import annotations

import pytest

from awe.models.pipeline import QualityGateConfig
from awe.models.task import TaskOutput
from awe.quality.gate import check, _check_format, _validate_against_schema, GateResult


@pytest.mark.asyncio
async def test_no_quality_gate():
    output = TaskOutput(raw_text="Hello")
    result = await check(output, None)
    assert result.passed


@pytest.mark.asyncio
async def test_empty_output_fails():
    output = TaskOutput(raw_text="   ")
    config = QualityGateConfig(mode="auto")
    result = await check(output, config)
    assert not result.passed
    assert "empty" in result.reason.lower()


@pytest.mark.asyncio
async def test_too_long_output_fails():
    output = TaskOutput(raw_text="x" * 200_001)
    config = QualityGateConfig(mode="auto")
    result = await check(output, config)
    assert not result.passed
    assert "too long" in result.reason.lower()


def test_schema_validation_pass():
    schema = {
        "properties": {
            "summary": {"type": "string"},
            "approved": {"type": "boolean"},
        },
        "required": ["summary", "approved"],
    }
    data = {"summary": "All good", "approved": True}
    result = _validate_against_schema(data, schema)
    assert result.passed


def test_schema_validation_missing_field():
    schema = {
        "properties": {"summary": {"type": "string"}},
        "required": ["summary"],
    }
    data = {"other_field": "value"}
    result = _validate_against_schema(data, schema)
    assert not result.passed
    assert "summary" in result.reason


def test_schema_validation_wrong_type():
    schema = {
        "properties": {"count": {"type": "integer"}},
    }
    data = {"count": "not a number"}
    result = _validate_against_schema(data, schema)
    assert not result.passed
    assert "count" in result.reason


@pytest.mark.asyncio
async def test_auto_mode_no_checks_passes():
    output = TaskOutput(raw_text="Some valid output")
    config = QualityGateConfig(mode="auto", checks=[])
    result = await check(output, config)
    assert result.passed
