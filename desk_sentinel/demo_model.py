"""Scripted model provider for keyless local demos.

Drives the real Strands agent event loop through read_status → decide_surface →
notify_human (or silent end_turn) without calling Bedrock, OpenAI, or Telegram.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncGenerator, AsyncIterable
from typing import Any

from pydantic import BaseModel
from typing_extensions import override

from strands.models.model import Model
from strands.types.content import Messages, SystemContentBlock
from strands.types.streaming import StreamEvent
from strands.types.tools import ToolChoice, ToolSpec


def _parse_tool_payload(content: list[dict[str, Any]]) -> Any:
    for item in content:
        if "json" in item:
            return item["json"]
        if "text" in item:
            text = item["text"].strip()
            if text.startswith("{") or text.startswith("["):
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return text
            return text
    return None


def _tool_results_by_name(messages: Messages) -> dict[str, Any]:
    """Map tool name → latest tool result payload."""
    pending: dict[str, str] = {}
    results: dict[str, Any] = {}

    for message in messages:
        for block in message.get("content", []):
            if "toolUse" in block:
                pending[block["toolUse"]["toolUseId"]] = block["toolUse"]["name"]
            if "toolResult" in block:
                tool_use_id = block["toolResult"]["toolUseId"]
                name = pending.get(tool_use_id)
                if not name:
                    continue
                payload = _parse_tool_payload(block["toolResult"].get("content", []))
                if payload is not None:
                    results[name] = payload

    return results


async def _emit_tool_call(name: str, inputs: dict[str, Any]) -> AsyncGenerator[StreamEvent, None]:
    tool_use_id = str(uuid.uuid4())
    payload = json.dumps(inputs)

    yield {"messageStart": {"role": "assistant"}}
    yield {
        "contentBlockStart": {
            "contentBlockIndex": 0,
            "start": {"toolUse": {"name": name, "toolUseId": tool_use_id}},
        }
    }
    yield {
        "contentBlockDelta": {
            "contentBlockIndex": 0,
            "delta": {"toolUse": {"input": payload}},
        }
    }
    yield {"contentBlockStop": {"contentBlockIndex": 0}}
    yield {"messageStop": {"stopReason": "tool_use"}}


async def _emit_text(text: str) -> AsyncGenerator[StreamEvent, None]:
    yield {"messageStart": {"role": "assistant"}}
    yield {"contentBlockStart": {"contentBlockIndex": 0, "start": {}}}
    yield {
        "contentBlockDelta": {
            "contentBlockIndex": 0,
            "delta": {"text": text},
        }
    }
    yield {"contentBlockStop": {"contentBlockIndex": 0}}
    yield {"messageStop": {"stopReason": "end_turn"}}


class DemoModel(Model):
    """Deterministic model that walks the Desk Sentinel tool chain."""

    def __init__(self) -> None:
        self._config: dict[str, Any] = {"context_window_limit": 8192, "model_id": "desk-sentinel-demo"}

    @override
    def update_config(self, **model_config: Any) -> None:
        self._config.update(model_config)

    @override
    def get_config(self) -> dict[str, Any]:
        return self._config

    @override
    def structured_output(
        self,
        output_model: type[BaseModel],
        prompt: Messages,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[dict[str, BaseModel | Any], None]:
        async def _gen() -> AsyncGenerator[dict[str, BaseModel | Any], None]:
            yield {"structured_output": None}

        return _gen()

    @override
    async def stream(
        self,
        messages: Messages,
        tool_specs: list[ToolSpec] | None = None,
        system_prompt: str | None = None,
        *,
        tool_choice: ToolChoice | None = None,
        system_prompt_content: list[SystemContentBlock] | None = None,
        invocation_state: dict[str, Any] | None = None,
        cancel_signal: Any | None = None,
        **kwargs: Any,
    ) -> AsyncIterable[StreamEvent]:
        state = invocation_state or {}
        fixture_path = state.get("fixture_path", "safe_hold_dry.json")
        results = _tool_results_by_name(messages)

        if "read_status" not in results:
            async for event in _emit_tool_call("read_status", {"fixture_path": fixture_path}):
                yield event
            return

        if "decide_surface" not in results:
            async for event in _emit_tool_call(
                "decide_surface",
                {"status": results["read_status"]},
            ):
                yield event
            return

        decision = results.get("decide_surface", {})
        if decision.get("action") == "notify" and "notify_human" not in results:
            async for event in _emit_tool_call(
                "notify_human",
                {
                    "decision": decision,
                    "message": decision.get("message", "Decision required."),
                },
            ):
                yield event
            return

        if decision.get("action") == "notify":
            text = "Alert delivered. Awaiting operator response."
        else:
            text = (
                "Silent watch — no human notification. "
                f"({decision.get('message', 'Routine monitoring.')})"
            )

        async for event in _emit_text(text):
            yield event
