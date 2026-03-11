"""Run API endpoints."""

from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sse_starlette.sse import EventSourceResponse

from awe.api.deps import get_db
from awe.api.schemas import RunDetail, RunSummary, SSEEvent, StepRunInfo
from awe.persistence.db import Database

router = APIRouter(prefix="/api/runs", tags=["runs"])


@router.get("", response_model=list[RunSummary])
async def list_runs(
    status: str | None = Query(None, description="Filter by status"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of runs"),
    db: Database = Depends(get_db),
) -> list[RunSummary]:
    """List pipeline execution history."""
    runs = await db.list_pipeline_runs(limit=limit)
    if status:
        runs = [r for r in runs if r["status"] == status]
    return [
        RunSummary(
            id=r["id"],
            pipeline_name=r["pipeline_name"],
            status=r["status"],
            created_at=r.get("created_at"),
            completed_at=r.get("completed_at"),
        )
        for r in runs
    ]


@router.get("/{run_id}", response_model=RunDetail)
async def get_run(
    run_id: str,
    db: Database = Depends(get_db),
) -> RunDetail:
    """Get details of a single pipeline run, including step runs."""
    run_data = await db.get_pipeline_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    step_runs = await db.get_step_runs(run_id)

    return RunDetail(
        id=run_data["id"],
        pipeline_name=run_data["pipeline_name"],
        status=run_data["status"],
        created_at=run_data.get("created_at"),
        completed_at=run_data.get("completed_at"),
        step_runs=[
            StepRunInfo(
                step_id=s["step_id"],
                agent_name=s.get("agent_name"),
                status=s["status"],
                attempt=s.get("attempt", 1),
                tokens_used=s.get("tokens_used", 0) or 0,
                cost_usd=s.get("cost_usd", 0.0) or 0.0,
                duration_ms=s.get("duration_ms", 0) or 0,
                failure_reason=s.get("failure_reason"),
            )
            for s in step_runs
        ],
    )


@router.get("/{run_id}/stream")
async def stream_run(
    run_id: str,
    db: Database = Depends(get_db),
) -> EventSourceResponse:
    """SSE stream of events for a pipeline run.

    Polls the events table every 500ms and sends new events to the client.
    Closes when the pipeline run reaches a terminal status (completed/failed).
    """
    run_data = await db.get_pipeline_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    async def event_generator():
        last_event_id = 0
        while True:
            events = await db.get_events(run_id)
            new_events = [e for e in events if e["id"] > last_event_id]

            for event in new_events:
                last_event_id = event["id"]
                payload = {}
                if event.get("payload"):
                    try:
                        payload = json.loads(event["payload"])
                    except (json.JSONDecodeError, TypeError):
                        payload = {}

                sse_event = SSEEvent(
                    event_type=event["event_type"],
                    step_id=event.get("step_id"),
                    payload=payload,
                    created_at=event.get("created_at"),
                )
                yield {
                    "event": event["event_type"],
                    "data": sse_event.model_dump_json(),
                }

            # Check if pipeline run is done
            run_data = await db.get_pipeline_run(run_id)
            if run_data and run_data["status"] in ("completed", "failed"):
                # Send final status event
                yield {
                    "event": "done",
                    "data": json.dumps({"status": run_data["status"]}),
                }
                return

            await asyncio.sleep(0.5)

    return EventSourceResponse(event_generator())
