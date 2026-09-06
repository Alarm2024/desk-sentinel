"""Read mock desk status from JSON fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from strands import tool

from desk_sentinel.config import FIXTURES_DIR


@tool
def read_status(fixture_path: str) -> dict:
    """Load the current dry-desk status snapshot from a local JSON fixture.

    Args:
        fixture_path: Path to a fixture file, or a bare fixture name under fixtures/.

    Returns:
        Parsed desk status dictionary (mock data only — no live trading APIs).
    """
    path = Path(fixture_path)
    if not path.is_absolute():
        candidate = FIXTURES_DIR / fixture_path
        if candidate.exists():
            path = candidate
        elif (FIXTURES_DIR / f"{fixture_path}.json").exists():
            path = FIXTURES_DIR / f"{fixture_path}.json"

    if not path.exists():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")

    return json.loads(path.read_text(encoding="utf-8"))
