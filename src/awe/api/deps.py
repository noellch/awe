"""FastAPI dependency injection."""

from __future__ import annotations

from pathlib import Path

from fastapi import Request

from awe.context.store import RawStore
from awe.persistence.db import Database


def get_db(request: Request) -> Database:
    """Get Database instance from app state."""
    return request.app.state.db


def get_store(request: Request) -> RawStore:
    """Get RawStore instance from app state."""
    return request.app.state.store


def get_pipeline_dirs(request: Request) -> list[Path]:
    """Get pipeline search directories from app state."""
    return request.app.state.pipeline_dirs


def get_agent_dirs(request: Request) -> list[Path]:
    """Get agent search directories from app state."""
    return request.app.state.agent_dirs
