"""AWE CLI - Command-line interface for Agent Workflow Engine."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from awe.config.loader import find_pipeline
from awe.context.store import RawStore
from awe.persistence.db import Database
from awe.runtime.agent_runtime import DirectAPIRuntime
from awe.runtime.pipeline_runtime import PipelineRunner

console = Console()

# Default paths
AWE_DIR = Path.cwd() / ".awe"
DB_PATH = AWE_DIR / "awe.db"
RUNS_DIR = AWE_DIR / "runs"
_PROJECT_ROOT = Path.cwd().parent if (Path.cwd().parent / "examples").is_dir() else Path.cwd()
PIPELINE_DIRS = [Path.cwd() / "pipelines", AWE_DIR / "pipelines", _PROJECT_ROOT / "examples" / "pipelines"]
AGENT_DIRS = [Path.cwd() / "agents", AWE_DIR / "agents", _PROJECT_ROOT / "examples" / "agents"]


@click.group()
@click.option(
    "--dir",
    "awe_dir",
    type=click.Path(path_type=Path),
    default=None,
    help="AWE working directory (default: .awe/)",
)
@click.pass_context
def main(ctx: click.Context, awe_dir: Path | None) -> None:
    """AWE - Agent Workflow Engine."""
    # Load .env file from current directory or AWE directory
    load_dotenv(Path.cwd() / ".env")
    if awe_dir:
        load_dotenv(awe_dir / ".env")

    ctx.ensure_object(dict)
    if awe_dir:
        ctx.obj["awe_dir"] = awe_dir
    else:
        ctx.obj["awe_dir"] = AWE_DIR


@main.command()
@click.argument("pipeline_name")
@click.option("--input", "input_json", default=None, help="Input data as JSON string")
@click.option(
    "--pipeline-dir",
    type=click.Path(path_type=Path, exists=True),
    default=None,
    help="Directory containing pipeline YAML files",
)
@click.option(
    "--agent-dir",
    type=click.Path(path_type=Path, exists=True),
    default=None,
    help="Directory containing agent YAML files",
)
@click.pass_context
def run(
    ctx: click.Context,
    pipeline_name: str,
    input_json: str | None,
    pipeline_dir: Path | None,
    agent_dir: Path | None,
) -> None:
    """Run a pipeline by name."""
    awe_dir: Path = ctx.obj["awe_dir"]

    pipeline_dirs = [pipeline_dir] if pipeline_dir else PIPELINE_DIRS
    agent_dirs = [agent_dir] if agent_dir else AGENT_DIRS

    input_data = json.loads(input_json) if input_json else None

    asyncio.run(_run_pipeline(awe_dir, pipeline_name, pipeline_dirs, agent_dirs, input_data))


async def _run_pipeline(
    awe_dir: Path,
    pipeline_name: str,
    pipeline_dirs: list[Path],
    agent_dirs: list[Path],
    input_data: dict | None,
) -> None:
    """Async pipeline execution."""
    # Load pipeline
    try:
        pipeline = find_pipeline(pipeline_name, pipeline_dirs)
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/] {e}")
        return

    # Initialize services
    db_path = awe_dir / "awe.db"
    runs_dir = awe_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    db = Database(db_path)
    await db.connect()

    try:
        store = RawStore(runs_dir)
        runtime = DirectAPIRuntime()
        runner = PipelineRunner(db, runtime, store, agent_dirs)
        await runner.run(pipeline, input_data)
    finally:
        await db.close()


@main.command()
@click.argument("run_id", required=False)
@click.pass_context
def status(ctx: click.Context, run_id: str | None) -> None:
    """Show status of a pipeline run, or list recent runs."""
    awe_dir: Path = ctx.obj["awe_dir"]
    asyncio.run(_show_status(awe_dir, run_id))


async def _show_status(awe_dir: Path, run_id: str | None) -> None:
    db_path = awe_dir / "awe.db"
    if not db_path.exists():
        console.print("[dim]No runs found. Run a pipeline first.[/]")
        return

    db = Database(db_path)
    await db.connect()

    try:
        if run_id:
            await _show_run_detail(db, run_id)
        else:
            await _show_run_list(db)
    finally:
        await db.close()


async def _show_run_list(db: Database) -> None:
    """Show list of recent pipeline runs."""
    runs = await db.list_pipeline_runs()
    if not runs:
        console.print("[dim]No runs found.[/]")
        return

    table = Table(title="Recent Pipeline Runs")
    table.add_column("Run ID", style="cyan")
    table.add_column("Pipeline", style="bold")
    table.add_column("Status")
    table.add_column("Created")

    for r in runs:
        status_style = {
            "completed": "[green]completed[/]",
            "running": "[blue]running[/]",
            "failed": "[red]failed[/]",
            "pending": "[dim]pending[/]",
        }.get(r["status"], r["status"])

        table.add_row(r["id"], r["pipeline_name"], status_style, r["created_at"])

    console.print(table)


async def _show_run_detail(db: Database, run_id: str) -> None:
    """Show detailed status of a specific pipeline run."""
    run_data = await db.get_pipeline_run(run_id)
    if not run_data:
        console.print(f"[red]Run '{run_id}' not found.[/]")
        return

    status_style = {
        "completed": "[green]completed[/]",
        "running": "[blue]running[/]",
        "failed": "[red]failed[/]",
        "pending": "[dim]pending[/]",
    }.get(run_data["status"], run_data["status"])

    console.print(f"\n[bold]Pipeline:[/] {run_data['pipeline_name']}")
    console.print(f"[bold]Run ID:[/]   {run_data['id']}")
    console.print(f"[bold]Status:[/]   {status_style}")
    console.print(f"[bold]Created:[/]  {run_data['created_at']}")
    if run_data.get("completed_at"):
        console.print(f"[bold]Completed:[/] {run_data['completed_at']}")

    # Show steps
    steps = await db.get_step_runs(run_id)
    if steps:
        console.print("\n[bold]Steps:[/]")
        table = Table(show_header=True)
        table.add_column("Step", style="bold")
        table.add_column("Agent")
        table.add_column("Status")
        table.add_column("Attempt")
        table.add_column("Tokens", justify="right")
        table.add_column("Cost", justify="right")
        table.add_column("Duration", justify="right")
        table.add_column("Failure Reason")

        for s in steps:
            step_status = {
                "passed": "[green]passed[/]",
                "running": "[blue]running[/]",
                "failed": "[red]failed[/]",
                "pending": "[dim]pending[/]",
            }.get(s["status"], s["status"])

            duration = f"{s['duration_ms']}ms" if s.get("duration_ms") else "-"
            cost = f"${s['cost_usd']:.4f}" if s.get("cost_usd") else "-"
            tokens = str(s.get("tokens_used") or "-")
            reason = (s.get("failure_reason") or "-")[:60]

            table.add_row(
                s["step_id"],
                s.get("agent_name") or "-",
                step_status,
                str(s.get("attempt", 1)),
                tokens,
                cost,
                duration,
                reason,
            )

        console.print(table)

    # Show total cost
    total_cost = sum(s.get("cost_usd") or 0 for s in steps)
    total_tokens = sum(s.get("tokens_used") or 0 for s in steps)
    console.print(f"\n[bold]Total:[/] {total_tokens} tokens, ${total_cost:.4f}")


@main.command(name="list")
@click.pass_context
def list_runs(ctx: click.Context) -> None:
    """List recent pipeline runs."""
    awe_dir: Path = ctx.obj["awe_dir"]
    asyncio.run(_show_status(awe_dir, None))
