"""Analyze dry bot exam/card text with Nebius Token Factory + NVIDIA Nemotron."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from desk_sentinel.config import ASSISTANT_SIGN, OWNER_SIGN
from desk_sentinel.nebius_eyes.client import chat_completion
from desk_sentinel.nebius_eyes.demo import demo_analyze

SYSTEM_PROMPT = """You are Morning Light Nebius Eyes — an honest dry-desk analyst.

You read dry bot "Exam/card" text from a solo operator's mock desk. You NEVER:
- recommend live trading, arming, or sending orders
- mention CLEAR+/go or auto-engage paths
- invent wallet keys, Telegram, or external APIs

You ALWAYS respond in English with exactly these six labeled lines (one field per line):
Test result: <pass/warn/fail style summary>
Signal: <what the card is saying>
Problem: <main issue or "None">
Needs: <what the human should do, if anything>
Alarms: <severity + brief note, or NONE>
Recommend: <one concrete next step on the dry desk>

Be concise, honest, and decision-grade. Mock fixtures only."""


def _extract_json_block(text: str) -> dict[str, Any] | None:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        data = json.loads(match.group())
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        return None
    return None


def _parse_labeled_lines(text: str) -> dict[str, str]:
    labels = {
        "test_result": r"test\s*result",
        "signal": r"signal",
        "problem": r"problem",
        "needs": r"needs",
        "alarms": r"alarms?",
        "recommend": r"recommend(?:ation)?",
    }
    found: dict[str, str] = {}
    for key, pattern in labels.items():
        m = re.search(
            rf"(?im)^\s*(?:\*\*)?{pattern}(?:\*\*)?\s*[:·\-]\s*(.+?)(?=^\s*(?:\*\*)?(?:test\s*result|signal|problem|needs|alarms?|recommend)|\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        if m:
            found[key] = m.group(1).strip().replace("\n", " ")
    return found


def _normalize_fields(raw: dict[str, Any]) -> dict[str, str]:
    mapping = {
        "test_result": ["test_result", "test result", "testResult"],
        "signal": ["signal"],
        "problem": ["problem"],
        "needs": ["needs"],
        "alarms": ["alarms", "alarm"],
        "recommend": ["recommend", "recommendation"],
    }
    out: dict[str, str] = {}
    lower_keys = {str(k).lower().replace(" ", "_"): v for k, v in raw.items()}
    for field, aliases in mapping.items():
        for alias in aliases:
            if alias in lower_keys:
                out[field] = str(lower_keys[alias]).strip()
                break
        if field not in out:
            out[field] = "—"
    return out


def analyze_exam_card(exam_card: str, *, mode: str | None = None) -> dict[str, str]:
    """Return structured analysis fields for exam card text."""
    mode = (mode or os.getenv("NEBIUS_EYES_MODE", "auto")).lower()
    use_live = mode == "live" or (mode == "auto" and os.getenv("NEBIUS_API_KEY"))

    if not use_live:
        return demo_analyze(exam_card)

    user_prompt = (
        "Analyze this dry bot Exam/card text. Return JSON with keys: "
        "test_result, signal, problem, needs, alarms, recommend.\n\n"
        f"--- exam card ---\n{exam_card.strip()}\n--- end ---"
    )

    raw = chat_completion(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
    )

    parsed = _extract_json_block(raw)
    if parsed:
        return _normalize_fields(parsed)

    labeled = _parse_labeled_lines(raw)
    if len(labeled) >= 4:
        return _normalize_fields(labeled)

    # Last resort: wrap free text
    return {
        "test_result": "REVIEW",
        "signal": raw[:200],
        "problem": "Model returned unstructured text",
        "needs": "Re-run or adjust NEBIUS_MODEL",
        "alarms": "INFO",
        "recommend": raw[-300:] if len(raw) > 300 else raw,
    }


def format_report(fields: dict[str, str], *, model_note: str = "") -> str:
    """Format branded report with owner/bot signs on separate lines."""
    lines = [
        OWNER_SIGN,
        "",
        "Morning Light Nebius Eyes",
        "─" * 32,
        f"Test result · {fields.get('test_result', '—')}",
        f"Signal · {fields.get('signal', '—')}",
        f"Problem · {fields.get('problem', '—')}",
        f"Needs · {fields.get('needs', '—')}",
        f"Alarms · {fields.get('alarms', '—')}",
        f"Recommend · {fields.get('recommend', '—')}",
    ]
    if model_note:
        lines.extend(["", model_note])
    lines.extend(["", ASSISTANT_SIGN])
    return "\n".join(lines)
