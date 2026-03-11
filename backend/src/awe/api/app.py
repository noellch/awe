"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from awe.context.store import RawStore
from awe.persistence.db import Database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database connection lifecycle."""
    db: Database = app.state.db
    await db.connect()
    yield
    await db.close()


def create_app(
    db_path: Path | None = None,
    runs_dir: Path | None = None,
    pipeline_dirs: list[Path] | None = None,
    agent_dirs: list[Path] | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application."""
    from awe.api.routers import agents, pipelines, runs

    # Defaults matching CLI conventions
    awe_dir = Path.cwd() / ".awe"

    _db_path = db_path or awe_dir / "awe.db"
    _runs_dir = runs_dir or awe_dir / "runs"
    _pipeline_dirs = pipeline_dirs or [
        Path.cwd() / "pipelines",
        awe_dir / "pipelines",
    ]
    _agent_dirs = agent_dirs or [
        Path.cwd() / "agents",
        awe_dir / "agents",
    ]

    _runs_dir.mkdir(parents=True, exist_ok=True)

    app = FastAPI(
        title="AWE - Agent Workflow Engine",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS (allow all for dev)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Store instances on app.state
    app.state.db = Database(_db_path)
    app.state.store = RawStore(_runs_dir)
    app.state.pipeline_dirs = _pipeline_dirs
    app.state.agent_dirs = _agent_dirs

    # Mount routers
    app.include_router(pipelines.router)
    app.include_router(runs.router)
    app.include_router(agents.router)

    return app
