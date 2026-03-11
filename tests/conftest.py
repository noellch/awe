"""Test configuration and fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture
def tmp_awe_dir(tmp_path):
    """Create a temporary AWE directory structure."""
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    return tmp_path
