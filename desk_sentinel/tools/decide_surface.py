"""Decide whether a desk state requires human attention."""

from __future__ import annotations

from strands import tool


@tool
def decide_surface(status: dict) -> dict:
    """Evaluate desk status and decide if the human should be notified.

    The agent stays silent for routine SAFE HOLD dry states. Surfaces decisions
    only for CLEAR go/no-go, SHORT market stance, or real faults.

    Args:
        status: Desk status payload from read_status.

    Returns:
        Decision record with action (silent|notify), surface, urgency, and message.
    """
    phase = status.get("phase", "").upper()
    health = status.get("health", "OK").upper()
    market_regime = status.get("market_regime", "").upper()
    dry_run = status.get("dry_run", True)

    if health == "FAULT":
        fault = status.get("fault", {})
        return {
            "action": "notify",
            "surface": "fault",
            "urgency": "critical",
            "dry_run": dry_run,
            "message": fault.get("summary", "Real fault detected on desk."),
            "recommended_action": fault.get("recommended_action", "Investigate immediately."),
        }

    if phase == "CLEAR" and status.get("ready", False):
        return {
            "action": "notify",
            "surface": "go_no_go",
            "urgency": "high",
            "dry_run": dry_run,
            "message": "Desk is CLEAR and ready — confirm go / no-go before live session.",
            "recommended_action": status.get("go_no_go_prompt", "Reply GO or NO-GO."),
        }

    if market_regime == "SHORT":
        return {
            "action": "notify",
            "surface": "go_no_go",
            "urgency": "medium",
            "dry_run": dry_run,
            "message": "SHORT market regime — confirm whether to engage or stand down.",
            "recommended_action": status.get("go_no_go_prompt", "Reply ENGAGE or STAND DOWN."),
        }

    if phase == "SAFE_HOLD" and dry_run:
        return {
            "action": "silent",
            "surface": None,
            "urgency": "none",
            "dry_run": dry_run,
            "message": "SAFE HOLD on dry desk — monitoring continues without interruption.",
            "recommended_action": None,
        }

    return {
        "action": "silent",
        "surface": None,
        "urgency": "none",
        "dry_run": dry_run,
        "message": "No decision surface — agent remains quiet.",
        "recommended_action": None,
    }
