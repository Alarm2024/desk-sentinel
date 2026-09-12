"""Nebius Token Factory client (OpenAI-compatible)."""

from __future__ import annotations

import os
from typing import Any

DEFAULT_BASE_URL = "https://api.tokenfactory.nebius.com/v1/"
DEFAULT_MODEL = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"


def get_nebius_config() -> dict[str, str]:
    return {
        "api_key": os.getenv("NEBIUS_API_KEY", ""),
        "base_url": os.getenv("NEBIUS_BASE_URL", DEFAULT_BASE_URL).rstrip("/") + "/",
        "model": os.getenv("NEBIUS_MODEL", DEFAULT_MODEL),
    }


def chat_completion(
    messages: list[dict[str, str]],
    *,
    temperature: float = 0.2,
    max_tokens: int = 800,
) -> str:
    """Call Nebius Token Factory chat completions."""
    cfg = get_nebius_config()
    if not cfg["api_key"]:
        raise RuntimeError(
            "NEBIUS_API_KEY is not set. Copy .env.example to .env or export the key."
        )

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "openai package required for live Nebius mode. "
            "Run: pip install openai"
        ) from exc

    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])
    response = client.chat.completions.create(
        model=cfg["model"],
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    choice = response.choices[0].message
    content = choice.content
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
            elif hasattr(block, "text"):
                parts.append(str(block.text))
        return "\n".join(parts).strip()
    return str(content or "").strip()


def list_models() -> list[dict[str, Any]]:
    """List models available on Token Factory (requires API key)."""
    cfg = get_nebius_config()
    if not cfg["api_key"]:
        raise RuntimeError("NEBIUS_API_KEY is not set.")

    from openai import OpenAI

    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])
    models = client.models.list()
    return [{"id": m.id} for m in models.data]
