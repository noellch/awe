"""Agent Runtime - protocol and implementations for executing agent tasks."""

from __future__ import annotations

import json as json_module
import time
from typing import Protocol

import anthropic

from awe.models.agent import AgentProfile
from awe.models.task import AssembledContext, Task, TaskOutput


class AgentRuntime(Protocol):
    """Protocol for agent execution backends."""

    async def execute(
        self,
        agent: AgentProfile,
        task: Task,
        context: AssembledContext,
    ) -> TaskOutput: ...


class DirectAPIRuntime:
    """Executes agent tasks by directly calling the Anthropic API."""

    def __init__(self) -> None:
        self.client = anthropic.AsyncAnthropic()

    async def execute(
        self,
        agent: AgentProfile,
        task: Task,
        context: AssembledContext,
    ) -> TaskOutput:
        """Execute a task by calling the Anthropic API.

        If the agent defines an output_schema, uses Anthropic's structured output
        (constrained decoding) to guarantee JSON schema compliance.
        """
        start_time = time.monotonic()

        messages = [{"role": "user", "content": context.user_prompt}]
        system_prompt = context.system_prompt or None

        if agent.output_schema:
            response = await self._execute_structured(agent, messages, system_prompt)
        else:
            response = await self._execute_plain(agent, messages, system_prompt)

        duration_ms = int((time.monotonic() - start_time) * 1000)

        raw_text = ""
        for block in response.content:
            if block.type == "text":
                raw_text += block.text

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        total_tokens = input_tokens + output_tokens
        cost = _estimate_cost(agent.model.id, input_tokens, output_tokens)

        # Parse structured output
        structured = _try_parse_json(raw_text)

        return TaskOutput(
            raw_text=raw_text,
            structured=structured,
            tokens_used=total_tokens,
            cost_usd=cost,
            duration_ms=duration_ms,
            model_id=agent.model.id,
        )

    async def _execute_plain(
        self,
        agent: AgentProfile,
        messages: list[dict],
        system_prompt: str | None,
    ) -> anthropic.types.Message:
        """Standard text completion."""
        return await self.client.messages.create(
            model=agent.model.id,
            max_tokens=agent.model.max_tokens,
            system=system_prompt if system_prompt else anthropic.NOT_GIVEN,
            messages=messages,
        )

    async def _execute_structured(
        self,
        agent: AgentProfile,
        messages: list[dict],
        system_prompt: str | None,
    ) -> anthropic.types.Message:
        """Structured output using constrained decoding.

        Uses Anthropic's output_format parameter to guarantee
        the response matches the agent's output_schema.
        """
        return await self.client.messages.create(
            model=agent.model.id,
            max_tokens=agent.model.max_tokens,
            system=system_prompt if system_prompt else anthropic.NOT_GIVEN,
            messages=messages,
            output_format={
                "type": "json",
                "schema": agent.output_schema,
            },
        )


def _estimate_cost(
    model_id: str, input_tokens: int, output_tokens: int
) -> float:
    """Estimate cost in USD based on model and token usage."""
    # Approximate pricing per million tokens (as of early 2026)
    pricing = {
        "claude-opus-4-6": (15.0, 75.0),
        "claude-sonnet-4-6": (3.0, 15.0),
        "claude-haiku-4-5-20251001": (0.80, 4.0),
    }
    input_rate, output_rate = pricing.get(model_id, (3.0, 15.0))
    return (input_tokens * input_rate + output_tokens * output_rate) / 1_000_000


def _try_parse_json(text: str) -> dict | None:
    """Try to parse JSON from agent output."""
    import json

    stripped = text.strip()

    # Try direct parse
    try:
        return json.loads(stripped)
    except (json.JSONDecodeError, ValueError):
        pass

    # Try extracting from markdown code block
    if "```json" in stripped:
        start = stripped.index("```json") + 7
        end = stripped.index("```", start)
        try:
            return json.loads(stripped[start:end].strip())
        except (json.JSONDecodeError, ValueError):
            pass

    return None
