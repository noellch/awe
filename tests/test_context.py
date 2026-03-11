"""Tests for Context Bus and Raw Store."""

from __future__ import annotations

from awe.context.store import RawStore


def test_raw_store_save_and_read(tmp_path):
    store = RawStore(tmp_path / "runs")
    path = store.save_output("run-1", "analyze", "# Analysis\nSome content here.")
    assert path.exists()
    content = store.read_output("run-1", "analyze")
    assert content == "# Analysis\nSome content here."


def test_raw_store_read_nonexistent(tmp_path):
    store = RawStore(tmp_path / "runs")
    assert store.read_output("run-1", "missing") is None


def test_raw_store_compressed(tmp_path):
    store = RawStore(tmp_path / "runs")
    store.save_output("run-1", "analyze", "Full output")
    store.save_compressed("run-1", "analyze", "summary", "Short summary")
    assert store.read_compressed("run-1", "analyze", "summary") == "Short summary"
    assert store.read_compressed("run-1", "analyze", "full") is None
