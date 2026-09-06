"""Mock human notification channel (console only — no Telegram/trading keys)."""

from __future__ import annotations

from datetime import datetime, timezone

from strands import tool

from desk_sentinel.config import get_settings


@tool
def notify_human(decision: dict, message: str) -> dict:
    """Deliver a decision-grade alert to the solo desk operator (mock channel).

    Args:
        decision: Structured decision from decide_surface.
        message: Human-readable alert body.

    Returns:
        Delivery receipt with timestamp and channel metadata.
    """
    settings = get_settings()
    timestamp = datetime.now(timezone.utc).isoformat()

    banner = (
        f"\n{'=' * 60}\n"
        f"  MORNING LIGHT DESK SENTINEL — HUMAN DECISION REQUIRED\n"
        f"  Owner {settings.owner_sign}  ·  Assistant {settings.assistant_sign}\n"
        f"  Operator: {settings.operator}\n"
        f"{'=' * 60}\n"
        f"  Surface : {decision.get('surface', 'unknown')}\n"
        f"  Urgency : {decision.get('urgency', 'unknown')}\n"
        f"  Dry run : {decision.get('dry_run', True)}\n"
        f"  Message : {message}\n"
    )
    if decision.get("recommended_action"):
        banner += f"  Action  : {decision['recommended_action']}\n"
    banner += f"{'=' * 60}\n"

    print(banner)

    return {
        "delivered": True,
        "channel": "mock_console",
        "timestamp": timestamp,
        "owner_sign": settings.owner_sign,
        "assistant_sign": settings.assistant_sign,
        "surface": decision.get("surface"),
        "urgency": decision.get("urgency"),
        "message": message,
    }
