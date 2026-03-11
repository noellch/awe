"""Context Bus - orchestrates context assembly for agent execution."""

from __future__ import annotations

from awe.context.compressor import compress
from awe.context.store import RawStore
from awe.models.agent import AgentProfile
from awe.models.pipeline import Pipeline, Step
from awe.models.task import AssembledContext, UpstreamContext


class ContextBus:
    """Assembles context from upstream steps for agent execution."""

    def __init__(self, store: RawStore) -> None:
        self.store = store

    async def assemble(
        self,
        pipeline: Pipeline,
        step: Step,
        agent: AgentProfile,
        run_id: str,
        input_data: dict | None = None,
        failure_reason: str | None = None,
    ) -> AssembledContext:
        """Assemble the full context for a step's execution."""
        # Build upstream context
        upstream_contexts: list[UpstreamContext] = []
        for ctx_from in step.context_from:
            raw = self.store.read_output(run_id, ctx_from.step)
            if raw is None:
                continue

            # Check if we already have a compressed version cached
            compressed = self.store.read_compressed(
                run_id, ctx_from.step, ctx_from.compress
            )
            if compressed is None:
                compressed = await compress(raw, ctx_from.compress)
                # Cache the compressed version
                if ctx_from.compress != "full":
                    self.store.save_compressed(
                        run_id, ctx_from.step, ctx_from.compress, compressed
                    )

            upstream_contexts.append(
                UpstreamContext(
                    step_id=ctx_from.step,
                    compress_strategy=ctx_from.compress,
                    content=compressed,
                )
            )

        # Build the user prompt
        user_prompt = _build_user_prompt(
            step=step,
            upstream_contexts=upstream_contexts,
            pipeline_context=pipeline.context,
            input_data=input_data,
            failure_reason=failure_reason,
        )

        return AssembledContext(
            system_prompt=agent.system_prompt,
            user_prompt=user_prompt,
            pipeline_context=pipeline.context,
            upstream_context=upstream_contexts,
        )


def _build_user_prompt(
    step: Step,
    upstream_contexts: list[UpstreamContext],
    pipeline_context: dict[str, str],
    input_data: dict | None = None,
    failure_reason: str | None = None,
) -> str:
    """Build the user prompt from all context sources."""
    parts: list[str] = []

    # Pipeline context
    if pipeline_context:
        ctx_str = "\n".join(f"- {k}: {v}" for k, v in pipeline_context.items())
        parts.append(f"## Pipeline Context\n{ctx_str}")

    # Upstream context
    for uc in upstream_contexts:
        label = f"From step '{uc.step_id}' ({uc.compress_strategy})"
        parts.append(f"## {label}\n{uc.content}")

    # Failure reason (for retries)
    if failure_reason:
        parts.append(
            f"## Previous Attempt Failed\nReason: {failure_reason}\nPlease address this issue in your response."
        )

    # The step's own prompt (with basic template substitution)
    prompt = step.prompt
    if input_data:
        for key, value in input_data.items():
            prompt = prompt.replace(f"{{{{input.{key}}}}}", str(value))

    parts.append(f"## Your Task\n{prompt}")

    return "\n\n".join(parts)
