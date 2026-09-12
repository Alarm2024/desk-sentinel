"""Offline demo analyzer — same output shape, no API key."""

from __future__ import annotations

import re
from typing import Any


def _pick(text: str, *patterns: str) -> str | None:
    lower = text.lower()
    for pattern in patterns:
        if pattern.lower() in lower:
            return pattern
    return None


def demo_analyze(exam_card: str) -> dict[str, str]:
    """Rule-based analysis for fixtures when NEBIUS_API_KEY is absent."""
    text = exam_card.strip()
    lower = text.lower()

    if "fault" in lower or "bridge" in lower and "timeout" in lower:
        return {
            "test_result": "FAIL — operational fault on dry desk",
            "signal": "Bridge heartbeat missing · execution lane halted",
            "problem": "EXEC_BRIDGE_TIMEOUT — mock bridge down 90s+",
            "needs": "Human ack · verify bridge process · restart dry lane",
            "alarms": "CRITICAL — do not proceed until bridge restored",
            "recommend": "Pause all dry sends. Restart bridge mock, re-run exam card.",
        }

    if "short" in lower and ("regime" in lower or "bearish" in lower):
        return {
            "test_result": "WARN — SHORT regime on dry desk",
            "signal": "Bearish breadth · thinning liquidity · wider spreads",
            "problem": "Regime shift detected — stance not confirmed",
            "needs": "Operator review of SHORT playbook (dry sim only)",
            "alarms": "MEDIUM — elevated slippage risk in sim",
            "recommend": "Stay in dry sim. Log stance. No live engagement.",
        }

    if "clear" in lower and ("ready" in lower or "go" in lower):
        return {
            "test_result": "ATTENTION — pre-flight complete on dry desk",
            "signal": "All checks green · decision window open (dry only)",
            "problem": "Operator decision pending — still dry run",
            "needs": "Explicit human review before any live arming",
            "alarms": "LOW — informational only (no auto-go)",
            "recommend": "Review checklist offline. This demo never arms live trading.",
        }

    if _pick(lower, "safe hold", "holding pattern", "no anomalies"):
        return {
            "test_result": "PASS — SAFE HOLD dry watch",
            "signal": "Neutral regime · stable liquidity · pre-open session",
            "problem": "None — routine dry holding pattern",
            "needs": "Continue silent watch · no operator action",
            "alarms": "NONE",
            "recommend": "Keep monitoring. Re-pulse exam card on next tick.",
        }

    # Generic fallback
    return {
        "test_result": "REVIEW — exam card parsed (demo mode)",
        "signal": _summarize_signal(text),
        "problem": "Unclassified card — human skim advised",
        "needs": "Set NEBIUS_API_KEY for NVIDIA model analysis",
        "alarms": "INFO — demo rules only",
        "recommend": "Re-run with live Nebius mode for Nemotron interpretation.",
    }


def _summarize_signal(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return "Empty exam card"
    snippet = " · ".join(lines[:3])
    return re.sub(r"\s+", " ", snippet)[:120]
