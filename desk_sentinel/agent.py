"""Build and run the Morning Light Desk Sentinel Strands agent."""

from __future__ import annotations

import os
from typing import Any

from strands import Agent

from desk_sentinel.config import get_settings
from desk_sentinel.demo_model import DemoModel
from desk_sentinel.tools import ALL_TOOLS

SYSTEM_PROMPT = """You are Morning Light Desk Sentinel, a professional desk-monitoring agent.

Your job is to quietly watch dry-desk status fixtures and ONLY interrupt the solo
operator when a real decision is needed: CLEAR go/no-go, SHORT market stance, or a
real fault. Never spam alerts for routine SAFE HOLD dry states.

Workflow:
1. Call read_status with the provided fixture path.
2. Call decide_surface with the status payload.
3. Call notify_human ONLY when decide_surface returns action=notify.
4. Otherwise finish silently with a brief confirmation — no notification.

You are monitoring mock fixtures only. Never request live trading keys or external APIs.
"""


def resolve_model():
    """Return a Strands model based on DESK_MODEL_MODE."""
    settings = get_settings()

    if settings.model_mode == "demo":
        return DemoModel()

    if settings.model_mode == "openai":
        from strands.models.openai import OpenAIModel

        model_id = os.getenv("OPENAI_MODEL_ID", "gpt-4o-mini")
        return OpenAIModel(model_id=model_id)

    if settings.model_mode == "bedrock":
        from strands.models.bedrock import BedrockModel

        model_id = os.getenv(
            "BEDROCK_MODEL_ID",
            "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        )
        return BedrockModel(model_id=model_id)

    raise ValueError(
        f"Unknown DESK_MODEL_MODE={settings.model_mode!r}. "
        "Use demo (default), openai, or bedrock."
    )


def create_agent() -> Agent:
    settings = get_settings()
    return Agent(
        model=resolve_model(),
        tools=ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
        name="Morning Light Desk Sentinel",
        description=(
            f"Quiet dry-desk monitor for {settings.operator}. "
            f"Owner {settings.owner_sign} · Assistant {settings.assistant_sign}"
        ),
    )


def run_watch(fixture_path: str) -> Any:
    """Run one monitoring cycle against a fixture."""
    agent = create_agent()

    return agent(
        (
            "Run one monitoring cycle for the desk fixture. "
            f"Fixture path: {fixture_path}. "
            "Notify the human only if decide_surface requires it."
        ),
        invocation_state={"fixture_path": fixture_path},
    )
