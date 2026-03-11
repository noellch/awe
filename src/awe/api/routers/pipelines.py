"""Pipeline API endpoints."""

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from awe.api.deps import get_agent_dirs, get_db, get_pipeline_dirs, get_store
from awe.api.schemas import PipelineDetail, PipelineSummary, RunCreateResponse, StepInfo
from awe.config.loader import find_pipeline, load_pipeline
from awe.context.store import RawStore
from awe.persistence.db import Database

router = APIRouter(prefix="/api/pipelines", tags=["pipelines"])


def _scan_pipelines(pipeline_dirs: list[Path]) -> list[tuple[Path, str]]:
    """Scan directories for pipeline YAML files, return (path, name) tuples."""
    results: list[tuple[Path, str]] = []
    seen: set[str] = set()
    for directory in pipeline_dirs:
        if not directory.exists():
            continue
        for ext in ("*.yaml", "*.yml"):
            for path in sorted(directory.glob(ext)):
                name = path.stem
                if name not in seen:
                    seen.add(name)
                    results.append((path, name))
    return results


@router.get("", response_model=list[PipelineSummary])
async def list_pipelines(
    pipeline_dirs: list[Path] = Depends(get_pipeline_dirs),
) -> list[PipelineSummary]:
    """List all available pipeline definitions."""
    summaries: list[PipelineSummary] = []
    for path, _name in _scan_pipelines(pipeline_dirs):
        try:
            pipeline = load_pipeline(path)
            summaries.append(
                PipelineSummary(
                    name=pipeline.name,
                    description=pipeline.description,
                    step_count=len(pipeline.steps),
                    file_path=str(path),
                )
            )
        except Exception:
            continue
    return summaries


@router.get("/{name}", response_model=PipelineDetail)
async def get_pipeline(
    name: str,
    pipeline_dirs: list[Path] = Depends(get_pipeline_dirs),
) -> PipelineDetail:
    """Get a single pipeline definition with steps."""
    try:
        pipeline = find_pipeline(name, pipeline_dirs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Pipeline '{name}' not found")
    return PipelineDetail(
        name=pipeline.name,
        description=pipeline.description,
        context=pipeline.context,
        steps=[
            StepInfo(id=s.id, agent=s.agent, prompt=s.prompt)
            for s in pipeline.steps
        ],
    )


@router.post("/{name}/run", response_model=RunCreateResponse)
async def run_pipeline(
    name: str,
    pipeline_dirs: list[Path] = Depends(get_pipeline_dirs),
    agent_dirs: list[Path] = Depends(get_agent_dirs),
    db: Database = Depends(get_db),
    store: RawStore = Depends(get_store),
) -> RunCreateResponse:
    """Start a pipeline execution in the background. Returns the run_id immediately."""
    try:
        pipeline = find_pipeline(name, pipeline_dirs)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Pipeline '{name}' not found")

    run_id = uuid.uuid4().hex[:12]
    await db.create_pipeline_run(run_id, pipeline.name)

    asyncio.create_task(_execute_pipeline(db, store, agent_dirs, pipeline, run_id))

    return RunCreateResponse(run_id=run_id)


async def _execute_pipeline(
    db: Database,
    store: RawStore,
    agent_dirs: list[Path],
    pipeline: object,
    run_id: str,
) -> None:
    """Background task to execute a pipeline."""
    try:
        from awe.runtime.agent_runtime import DirectAPIRuntime
        from awe.runtime.pipeline_runtime import PipelineRunner

        runtime = DirectAPIRuntime()
        runner = PipelineRunner(db, runtime, store, agent_dirs)
        await runner.run(pipeline, None)  # type: ignore[arg-type]
    except Exception:
        await db.update_pipeline_status(run_id, "failed")
