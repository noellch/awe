"""SQLite persistence layer for pipeline state and events."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id TEXT PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    context TEXT,
    input TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS step_runs (
    id TEXT PRIMARY KEY,
    pipeline_run_id TEXT NOT NULL REFERENCES pipeline_runs(id),
    step_id TEXT NOT NULL,
    agent_name TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    attempt INTEGER DEFAULT 1,
    output_path TEXT,
    tokens_used INTEGER DEFAULT 0,
    cost_usd REAL DEFAULT 0.0,
    duration_ms INTEGER DEFAULT 0,
    failure_reason TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_run_id TEXT NOT NULL REFERENCES pipeline_runs(id),
    step_id TEXT,
    event_type TEXT NOT NULL,
    payload TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
"""


class Database:
    """Async SQLite database for AWE state management."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        """Connect to the database and initialize schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(str(self.db_path))
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.executescript(SCHEMA)
        await self._conn.commit()

    async def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._conn

    # --- Pipeline Runs ---

    async def create_pipeline_run(
        self,
        run_id: str,
        pipeline_name: str,
        context: dict | None = None,
        input_data: dict | None = None,
    ) -> None:
        await self.conn.execute(
            "INSERT INTO pipeline_runs (id, pipeline_name, status, context, input) VALUES (?, ?, 'running', ?, ?)",
            (run_id, pipeline_name, json.dumps(context), json.dumps(input_data)),
        )
        await self.conn.commit()

    async def update_pipeline_status(
        self, run_id: str, status: str
    ) -> None:
        completed = (
            datetime.now(timezone.utc).isoformat()
            if status in ("completed", "failed")
            else None
        )
        await self.conn.execute(
            "UPDATE pipeline_runs SET status = ?, completed_at = ? WHERE id = ?",
            (status, completed, run_id),
        )
        await self.conn.commit()

    async def get_pipeline_run(self, run_id: str) -> dict | None:
        cursor = await self.conn.execute(
            "SELECT * FROM pipeline_runs WHERE id = ?", (run_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None

    async def list_pipeline_runs(self, limit: int = 20) -> list[dict]:
        cursor = await self.conn.execute(
            "SELECT * FROM pipeline_runs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    # --- Step Runs ---

    async def create_step_run(
        self,
        step_run_id: str,
        pipeline_run_id: str,
        step_id: str,
        agent_name: str,
        attempt: int = 1,
    ) -> None:
        await self.conn.execute(
            "INSERT INTO step_runs (id, pipeline_run_id, step_id, agent_name, status, attempt) VALUES (?, ?, ?, ?, 'running', ?)",
            (step_run_id, pipeline_run_id, step_id, agent_name, attempt),
        )
        await self.conn.commit()

    async def update_step_run(
        self, step_run_id: str, **kwargs: str | int | float | None
    ) -> None:
        if not kwargs:
            return
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values())
        values.append(step_run_id)
        await self.conn.execute(
            f"UPDATE step_runs SET {sets} WHERE id = ?",  # noqa: S608
            values,
        )
        await self.conn.commit()

    async def get_step_runs(self, pipeline_run_id: str) -> list[dict]:
        cursor = await self.conn.execute(
            "SELECT * FROM step_runs WHERE pipeline_run_id = ? ORDER BY created_at",
            (pipeline_run_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]

    # --- Events ---

    async def log_event(
        self,
        pipeline_run_id: str,
        event_type: str,
        step_id: str | None = None,
        payload: dict | None = None,
    ) -> None:
        await self.conn.execute(
            "INSERT INTO events (pipeline_run_id, step_id, event_type, payload) VALUES (?, ?, ?, ?)",
            (pipeline_run_id, step_id, event_type, json.dumps(payload)),
        )
        await self.conn.commit()

    async def get_events(
        self, pipeline_run_id: str, step_id: str | None = None
    ) -> list[dict]:
        if step_id:
            cursor = await self.conn.execute(
                "SELECT * FROM events WHERE pipeline_run_id = ? AND step_id = ? ORDER BY created_at",
                (pipeline_run_id, step_id),
            )
        else:
            cursor = await self.conn.execute(
                "SELECT * FROM events WHERE pipeline_run_id = ? ORDER BY created_at",
                (pipeline_run_id,),
            )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
