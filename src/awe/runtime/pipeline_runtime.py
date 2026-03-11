"""Pipeline Runtime - the main orchestration engine."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console

from awe.config.loader import find_agent
from awe.context.bus import ContextBus
from awe.context.store import RawStore
from awe.models.agent import AgentProfile
from awe.models.pipeline import Pipeline, Step
from awe.models.task import Task, TaskOutput, TaskStatus
from awe.persistence.db import Database
from awe.quality.gate import GateResult, check as quality_check
from awe.runtime.agent_runtime import AgentRuntime

console = Console()


class PipelineRunner:
    """Executes a pipeline end-to-end."""

    def __init__(
        self,
        db: Database,
        agent_runtime: AgentRuntime,
        store: RawStore,
        agent_dirs: list[Path],
    ) -> None:
        self.db = db
        self.agent_runtime = agent_runtime
        self.store = store
        self.agent_dirs = agent_dirs
        self.context_bus = ContextBus(store)

    async def run(
        self,
        pipeline: Pipeline,
        input_data: dict | None = None,
    ) -> str:
        """Execute a pipeline and return the run ID."""
        run_id = _generate_run_id()

        await self.db.create_pipeline_run(
            run_id=run_id,
            pipeline_name=pipeline.name,
            context=pipeline.context,
            input_data=input_data,
        )
        await self.db.log_event(run_id, "pipeline_started", payload={"pipeline": pipeline.name})

        console.print(f"\n[bold blue]Pipeline:[/] {pipeline.name}")
        console.print(f"[bold blue]Run ID:[/]   {run_id}\n")

        try:
            for step_id in pipeline.step_order():
                step = pipeline.get_step(step_id)
                success = await self._execute_step(pipeline, step, run_id, input_data)
                if not success:
                    await self.db.update_pipeline_status(run_id, "failed")
                    await self.db.log_event(run_id, "pipeline_failed", step_id=step_id)
                    console.print(f"\n[bold red]Pipeline failed at step '{step_id}'[/]")
                    return run_id

            await self.db.update_pipeline_status(run_id, "completed")
            await self.db.log_event(run_id, "pipeline_completed")
            console.print("\n[bold green]Pipeline completed successfully![/]")

        except Exception as e:
            await self.db.update_pipeline_status(run_id, "failed")
            await self.db.log_event(
                run_id, "pipeline_error", payload={"error": str(e)}
            )
            console.print(f"\n[bold red]Pipeline error: {e}[/]")
            raise

        return run_id

    async def _execute_step(
        self,
        pipeline: Pipeline,
        step: Step,
        run_id: str,
        input_data: dict | None,
    ) -> bool:
        """Execute a single step with retry logic. Returns True if passed."""
        agent = find_agent(step.agent, self.agent_dirs)
        max_attempts = step.retry.max_retries + 1
        failure_reason: str | None = None

        for attempt in range(1, max_attempts + 1):
            step_run_id = f"{run_id}_{step.id}_a{attempt}"

            console.print(
                f"  [bold]Step:[/] {step.id}  "
                f"[dim]agent={agent.name} attempt={attempt}/{max_attempts}[/]"
            )

            await self.db.create_step_run(
                step_run_id=step_run_id,
                pipeline_run_id=run_id,
                step_id=step.id,
                agent_name=agent.name,
                attempt=attempt,
            )
            await self.db.log_event(
                run_id, "step_started", step_id=step.id,
                payload={"attempt": attempt, "agent": agent.name},
            )

            # Assemble context
            context = await self.context_bus.assemble(
                pipeline=pipeline,
                step=step,
                agent=agent,
                run_id=run_id,
                input_data=input_data,
                failure_reason=failure_reason if attempt > 1 else None,
            )

            # Execute
            task = Task(
                step_id=step.id,
                pipeline_run_id=run_id,
                agent_name=agent.name,
                prompt=step.prompt,
                attempt=attempt,
                failure_reason=failure_reason,
            )

            try:
                output = await self.agent_runtime.execute(agent, task, context)
            except Exception as e:
                failure_reason = f"Agent execution error: {e}"
                await self.db.update_step_run(
                    step_run_id,
                    status="failed",
                    failure_reason=failure_reason,
                )
                await self.db.log_event(
                    run_id, "step_failed", step_id=step.id,
                    payload={"reason": failure_reason, "attempt": attempt},
                )
                console.print(f"    [red]Error: {e}[/]")
                continue

            # Save output
            self.store.save_output(run_id, step.id, output.raw_text)
            if output.structured:
                import json
                self.store.save_structured(
                    run_id, step.id, json.dumps(output.structured, indent=2)
                )

            # Quality gate
            gate_result = await quality_check(
                output, step.quality_gate, agent.output_schema
            )

            await self.db.update_step_run(
                step_run_id,
                status="passed" if gate_result.passed else "failed",
                output_path=str(self.store._step_dir(run_id, step.id)),
                tokens_used=output.tokens_used,
                cost_usd=output.cost_usd,
                duration_ms=output.duration_ms,
                failure_reason=gate_result.reason if not gate_result.passed else None,
                completed_at=datetime.now(timezone.utc).isoformat(),
            )

            if gate_result.passed:
                await self.db.log_event(
                    run_id, "step_passed", step_id=step.id,
                    payload={
                        "tokens": output.tokens_used,
                        "cost": output.cost_usd,
                        "duration_ms": output.duration_ms,
                    },
                )
                console.print(
                    f"    [green]Passed[/] "
                    f"[dim]({output.duration_ms}ms, {output.tokens_used} tokens, ${output.cost_usd:.4f})[/]"
                )
                return True

            # Failed quality gate
            failure_reason = gate_result.reason
            await self.db.log_event(
                run_id, "quality_gate_failed", step_id=step.id,
                payload={"reason": failure_reason, "phase": gate_result.phase, "attempt": attempt},
            )
            console.print(f"    [yellow]Quality gate failed: {failure_reason}[/]")

            if attempt < max_attempts:
                console.print(f"    [dim]Retrying...[/]")

        # All attempts exhausted
        await self.db.log_event(
            run_id, "step_aborted", step_id=step.id,
            payload={"max_attempts": max_attempts},
        )
        console.print(f"    [red]Aborted after {max_attempts} attempts[/]")
        return False


def _generate_run_id() -> str:
    """Generate a human-readable run ID."""
    now = datetime.now(timezone.utc)
    short_uuid = uuid.uuid4().hex[:6]
    return f"run-{now.strftime('%Y%m%d-%H%M%S')}-{short_uuid}"
