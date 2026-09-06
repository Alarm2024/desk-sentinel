"""CLI entry point for Morning Light Desk Sentinel demos."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from typing import Any

from desk_sentinel.agent import run_watch
from desk_sentinel.config import FIXTURES_DIR, get_settings


DEFAULT_FIXTURES = [
    "safe_hold_dry.json",
    "clear_ready.json",
    "short_market.json",
    "real_fault.json",
]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="desk_sentinel",
        description="Morning Light Desk Sentinel — Strands dry-desk monitor (mock fixtures only)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="Run a monitoring cycle against fixture(s)")
    demo.add_argument(
        "--fixture",
        default="safe_hold_dry.json",
        help="Fixture file name or path (default: safe_hold_dry.json)",
    )
    demo.add_argument(
        "--all",
        action="store_true",
        help="Run all bundled demo fixtures sequentially",
    )
    return parser


def _extract_message(result: Any) -> str:
    message = getattr(result, "message", result)
    if isinstance(message, dict):
        for block in message.get("content", []):
            if isinstance(block, dict) and block.get("text"):
                return block["text"]
    if isinstance(result, dict):
        for block in result.get("content", []):
            if isinstance(block, dict) and block.get("text"):
                return block["text"]
    return str(result)


def _run_fixture(fixture: str) -> None:
    settings = get_settings()
    path = Path(fixture)
    if not path.is_absolute() and not path.exists():
        path = FIXTURES_DIR / fixture

    print(f"\n--- fixture: {path.name} ---")
    print(f"Owner {settings.owner_sign} · Assistant {settings.assistant_sign}")
    print(f"Operator: {settings.operator}")
    print(f"Model mode: {settings.model_mode}\n")

    result = run_watch(str(path if path.exists() else fixture))
    print(f"\nAgent result: {_extract_message(result)}\n")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "demo":
        if args.all:
            for fixture in DEFAULT_FIXTURES:
                _run_fixture(fixture)
        else:
            _run_fixture(args.fixture)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
