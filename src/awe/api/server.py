"""AWE API server entry point."""

from __future__ import annotations

from pathlib import Path

import uvicorn
from dotenv import load_dotenv


def main() -> None:
    """Start the AWE API server."""
    load_dotenv(Path.cwd() / ".env")

    uvicorn.run(
        "awe.api.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
