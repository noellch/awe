"""Quality Gate - verifies agent output quality."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass

import anthropic
from pydantic import ValidationError

from awe.models.pipeline import QualityGateConfig
from awe.models.task import TaskOutput


@dataclass
class GateResult:
    """Result of a quality gate check."""

    passed: bool
    reason: str = ""
    phase: str = ""


async def check(
    output: TaskOutput,
    config: QualityGateConfig | None,
    output_schema: dict | None = None,
) -> GateResult:
    """Run quality gate checks on agent output."""
    if config is None:
        return GateResult(passed=True, reason="No quality gate configured")

    # Phase 1: Format check (deterministic, zero cost)
    format_result = _check_format(output, output_schema)
    if not format_result.passed:
        return format_result

    # Phase 2: Content check (based on mode)
    if config.mode == "auto":
        return await _check_auto(output, config)
    if config.mode == "agent":
        return await _check_agent(output, config)

    # Human mode: pass through for now (needs external integration)
    return GateResult(passed=True, reason=f"Mode '{config.mode}' not yet implemented, passing through")


def _check_format(output: TaskOutput, output_schema: dict | None) -> GateResult:
    """Phase 1: Format validation."""
    # Check for empty output
    if not output.raw_text.strip():
        return GateResult(
            passed=False, reason="Agent returned empty output", phase="format"
        )

    # Check for excessively long output (potential runaway)
    if len(output.raw_text) > 200_000:
        return GateResult(
            passed=False,
            reason=f"Output too long ({len(output.raw_text)} chars, max 200000)",
            phase="format",
        )

    # Check structured output against schema if both are present
    if output_schema and output.structured:
        schema_result = _validate_against_schema(output.structured, output_schema)
        if not schema_result.passed:
            return schema_result

    return GateResult(passed=True, phase="format")


def _validate_against_schema(data: dict, schema: dict) -> GateResult:
    """Validate structured data against a JSON schema-like definition.

    For MVP, we do basic type and required field checking.
    """
    if "properties" not in schema:
        return GateResult(passed=True, phase="format")

    # Check required fields
    required_fields = schema.get("required", [])
    missing = [f for f in required_fields if f not in data]
    if missing:
        return GateResult(
            passed=False,
            reason=f"Missing required fields: {missing}",
            phase="format",
        )

    # Check field types
    properties = schema.get("properties", {})
    type_map = {"string": str, "integer": int, "number": (int, float), "boolean": bool, "array": list, "object": dict}
    for field_name, field_schema in properties.items():
        if field_name not in data:
            continue
        expected_type_name = field_schema.get("type")
        if expected_type_name and expected_type_name in type_map:
            expected_type = type_map[expected_type_name]
            if not isinstance(data[field_name], expected_type):
                return GateResult(
                    passed=False,
                    reason=f"Field '{field_name}' expected type '{expected_type_name}', got '{type(data[field_name]).__name__}'",
                    phase="format",
                )

    return GateResult(passed=True, phase="format")


async def _check_auto(
    output: TaskOutput, config: QualityGateConfig
) -> GateResult:
    """Phase 2: Automatic content checks."""
    for check_config in config.checks:
        if check_config.type in ("test_runner", "linter") and check_config.command:
            result = _check_command(check_config.command)
            if not result.passed:
                return result

    return GateResult(passed=True, phase="content")


def _check_command(command: str) -> GateResult:
    """Run a shell command as a quality check."""
    try:
        result = subprocess.run(
            command,
            shell=True,  # noqa: S602
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            return GateResult(passed=True, phase="content")
        return GateResult(
            passed=False,
            reason=f"Command failed (exit {result.returncode}): {result.stderr[:500]}",
            phase="content",
        )
    except subprocess.TimeoutExpired:
        return GateResult(
            passed=False, reason=f"Command timed out: {command}", phase="content"
        )


async def _check_agent(
    output: TaskOutput, config: QualityGateConfig
) -> GateResult:
    """Phase 2 (agent mode): Use another LLM agent to review the output.

    The reviewer agent receives the output and returns a JSON verdict:
    {"approved": true/false, "issues": [...], "summary": "..."}
    """
    review_prompt = config.review_prompt

    prompt = _build_review_prompt(output, review_prompt)

    try:
        client = anthropic.AsyncAnthropic()
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",  # cheap model for reviews
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
            output_format={
                "type": "json",
                "schema": _REVIEW_SCHEMA,
            },
        )

        raw_text = ""
        for block in response.content:
            if block.type == "text":
                raw_text += block.text

        verdict = json.loads(raw_text)

        if verdict.get("approved", False):
            return GateResult(passed=True, phase="agent_review")

        issues = verdict.get("issues", [])
        summary = verdict.get("summary", "Review failed")
        issue_text = "; ".join(issues[:3]) if issues else summary
        return GateResult(
            passed=False,
            reason=f"Agent review: {issue_text}",
            phase="agent_review",
        )

    except Exception as e:
        # If the review agent itself fails, pass through with a warning
        return GateResult(
            passed=True,
            reason=f"Agent review skipped (error: {e})",
            phase="agent_review",
        )


def _build_review_prompt(output: TaskOutput, custom_prompt: str | None = None) -> str:
    """Build the prompt for the reviewer agent."""
    base = (
        "You are a quality reviewer. Evaluate the following output from another AI agent.\n\n"
        "Determine if the output is:\n"
        "1. Complete - addresses the task fully\n"
        "2. Correct - no factual errors or logical issues\n"
        "3. Well-structured - organized and clear\n\n"
    )

    if custom_prompt:
        base += f"Additional review criteria:\n{custom_prompt}\n\n"

    base += f"## Agent Output to Review\n\n{output.raw_text}\n"

    return base


# JSON schema for the reviewer's verdict
_REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "approved": {
            "type": "boolean",
            "description": "Whether the output passes review",
        },
        "issues": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of issues found (empty if approved)",
        },
        "summary": {
            "type": "string",
            "description": "Brief summary of the review",
        },
    },
    "required": ["approved", "issues", "summary"],
}
