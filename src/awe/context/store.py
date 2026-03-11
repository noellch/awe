"""Raw Store - filesystem-based storage for agent outputs."""

from __future__ import annotations

from pathlib import Path


class RawStore:
    """Stores and retrieves raw agent outputs on the filesystem."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def _step_dir(self, run_id: str, step_id: str) -> Path:
        return self.base_dir / run_id / step_id

    def save_output(self, run_id: str, step_id: str, content: str) -> Path:
        """Save raw output to filesystem. Returns the file path."""
        step_dir = self._step_dir(run_id, step_id)
        step_dir.mkdir(parents=True, exist_ok=True)
        output_path = step_dir / "output.md"
        output_path.write_text(content, encoding="utf-8")
        return output_path

    def save_structured(self, run_id: str, step_id: str, content: str) -> Path:
        """Save structured JSON output to filesystem."""
        step_dir = self._step_dir(run_id, step_id)
        step_dir.mkdir(parents=True, exist_ok=True)
        output_path = step_dir / "output.json"
        output_path.write_text(content, encoding="utf-8")
        return output_path

    def save_compressed(
        self, run_id: str, step_id: str, strategy: str, content: str
    ) -> Path:
        """Save a compressed version of the output."""
        compressed_dir = self._step_dir(run_id, step_id) / "compressed"
        compressed_dir.mkdir(parents=True, exist_ok=True)
        output_path = compressed_dir / f"{strategy}.md"
        output_path.write_text(content, encoding="utf-8")
        return output_path

    def read_output(self, run_id: str, step_id: str) -> str | None:
        """Read raw output for a step."""
        output_path = self._step_dir(run_id, step_id) / "output.md"
        if output_path.exists():
            return output_path.read_text(encoding="utf-8")
        return None

    def read_compressed(
        self, run_id: str, step_id: str, strategy: str
    ) -> str | None:
        """Read a compressed version of a step's output."""
        path = self._step_dir(run_id, step_id) / "compressed" / f"{strategy}.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None
