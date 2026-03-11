"""Tests for the AWE API layer."""

from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from awe.api.app import create_app

EXAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "examples"


@pytest.fixture
async def client(tmp_path: Path):
    """Create a test client with temporary database and example dirs."""
    db_path = tmp_path / "test.db"
    runs_dir = tmp_path / "runs"
    pipeline_dirs = [EXAMPLES_DIR / "pipelines"]
    agent_dirs = [EXAMPLES_DIR / "agents"]

    app = create_app(
        db_path=db_path,
        runs_dir=runs_dir,
        pipeline_dirs=pipeline_dirs,
        agent_dirs=agent_dirs,
    )

    # Manually connect DB since ASGITransport doesn't trigger lifespan
    await app.state.db.connect()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    await app.state.db.close()


@pytest.mark.asyncio
async def test_list_pipelines(client: AsyncClient):
    """GET /api/pipelines should return the example pipeline."""
    resp = await client.get("/api/pipelines")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    names = [p["name"] for p in data]
    assert "analyze-and-fix" in names
    # Check structure
    pipeline = next(p for p in data if p["name"] == "analyze-and-fix")
    assert pipeline["step_count"] == 2
    assert "file_path" in pipeline


@pytest.mark.asyncio
async def test_get_pipeline(client: AsyncClient):
    """GET /api/pipelines/{name} should return pipeline details."""
    resp = await client.get("/api/pipelines/analyze-and-fix")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "analyze-and-fix"
    assert len(data["steps"]) == 2
    assert data["steps"][0]["id"] == "analyze"
    assert data["steps"][1]["id"] == "fix"


@pytest.mark.asyncio
async def test_get_pipeline_not_found(client: AsyncClient):
    """GET /api/pipelines/{name} should return 404 for missing pipeline."""
    resp = await client.get("/api/pipelines/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_agents(client: AsyncClient):
    """GET /api/agents should return example agents."""
    resp = await client.get("/api/agents")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    names = {a["name"] for a in data}
    assert "researcher" in names
    assert "coder" in names


@pytest.mark.asyncio
async def test_get_agent(client: AsyncClient):
    """GET /api/agents/{name} should return a single agent."""
    resp = await client.get("/api/agents/researcher")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "researcher"
    assert "analysis" in data["capabilities_tags"]


@pytest.mark.asyncio
async def test_get_agent_not_found(client: AsyncClient):
    """GET /api/agents/{name} should return 404 for missing agent."""
    resp = await client.get("/api/agents/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_runs_empty(client: AsyncClient):
    """GET /api/runs should return empty list when no runs exist."""
    resp = await client.get("/api/runs")
    assert resp.status_code == 200
    data = resp.json()
    assert data == []


@pytest.mark.asyncio
async def test_get_run_not_found(client: AsyncClient):
    """GET /api/runs/{run_id} should return 404 for missing run."""
    resp = await client.get("/api/runs/nonexistent")
    assert resp.status_code == 404
