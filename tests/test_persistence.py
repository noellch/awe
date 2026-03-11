"""Tests for SQLite persistence layer."""

from __future__ import annotations

import pytest
import pytest_asyncio

from awe.persistence.db import Database


@pytest_asyncio.fixture
async def db(tmp_path):
    """Create a temporary database."""
    db = Database(tmp_path / "test.db")
    await db.connect()
    yield db
    await db.close()


@pytest.mark.asyncio
async def test_create_and_get_pipeline_run(db):
    await db.create_pipeline_run(
        run_id="test-run-001",
        pipeline_name="test-pipeline",
        context={"repo": "rubato"},
        input_data={"problem": "something broke"},
    )
    run = await db.get_pipeline_run("test-run-001")
    assert run is not None
    assert run["pipeline_name"] == "test-pipeline"
    assert run["status"] == "running"


@pytest.mark.asyncio
async def test_update_pipeline_status(db):
    await db.create_pipeline_run("run-1", "test")
    await db.update_pipeline_status("run-1", "completed")
    run = await db.get_pipeline_run("run-1")
    assert run["status"] == "completed"
    assert run["completed_at"] is not None


@pytest.mark.asyncio
async def test_step_runs(db):
    await db.create_pipeline_run("run-1", "test")
    await db.create_step_run("run-1_analyze_a1", "run-1", "analyze", "researcher")
    await db.update_step_run(
        "run-1_analyze_a1",
        status="passed",
        tokens_used=1500,
        cost_usd=0.02,
        duration_ms=3200,
    )
    steps = await db.get_step_runs("run-1")
    assert len(steps) == 1
    assert steps[0]["status"] == "passed"
    assert steps[0]["tokens_used"] == 1500


@pytest.mark.asyncio
async def test_events(db):
    await db.create_pipeline_run("run-1", "test")
    await db.log_event("run-1", "pipeline_started", payload={"pipeline": "test"})
    await db.log_event("run-1", "step_started", step_id="analyze")

    events = await db.get_events("run-1")
    assert len(events) == 2
    assert events[0]["event_type"] == "pipeline_started"

    step_events = await db.get_events("run-1", step_id="analyze")
    assert len(step_events) == 1


@pytest.mark.asyncio
async def test_list_pipeline_runs(db):
    await db.create_pipeline_run("run-1", "pipeline-a")
    await db.create_pipeline_run("run-2", "pipeline-b")
    runs = await db.list_pipeline_runs()
    assert len(runs) == 2
