from __future__ import annotations

import json
from typing import Any

from app.domain.conversation import (
    AssistantMessage,
    ErrorItem,
    ToolCall,
    ToolResult,
    UserMessage,
)
from app.domain.model import ModelRequest, ModelResponse, ToolCallParams
from app.domain.tools import ToolDefinition
from app.infrastructure.openrouter.dto import (
    ChatResponseDto,
    ToolDto,
    ToolFunctionDto,
)


def to_api_payload(request: ModelRequest, model: str) -> dict[str, Any]:
    """Build the JSON body to POST to OpenRouter /chat/completions."""
    payload: dict[str, Any] = {
        "model": model,
        "messages": _build_messages(request.messages),
    }
    if request.tools:
        payload["tools"] = _build_tools(request.tools)
        payload["tool_choice"] = "auto"
    return payload


def to_model_response(dto: ChatResponseDto) -> ModelResponse:
    """Parse the OpenRouter response into a domain ModelResponse."""
    msg = dto.choices[0].message

    if msg.tool_calls:
        tool_calls = [
            ToolCallParams(
                tool_call_id=tc.id,
                tool_name=tc.function.name,
                arguments=json.loads(tc.function.arguments),
            )
            for tc in msg.tool_calls
        ]
        return ModelResponse(tool_calls=tool_calls)

    return ModelResponse(content=msg.content or "")


def _build_messages(items: list) -> list[dict[str, Any]]:
    """
    Convert domain conversation items to the OpenAI message array.

    Consecutive ToolCall items are collapsed into a single assistant message
    with a tool_calls array — this mirrors how the model originally produced them.
    ErrorItems are skipped (UI-only, not part of model context).
    """
    result: list[dict[str, Any]] = []
    i = 0
    while i < len(items):
        item = items[i]

        if isinstance(item, UserMessage):
            result.append({"role": "user", "content": item.content})
            i += 1

        elif isinstance(item, AssistantMessage):
            result.append({"role": "assistant", "content": item.content})
            i += 1

        elif isinstance(item, ToolCall):
            # Collect all back-to-back ToolCall items (same assistant turn).
            tool_calls_payload: list[dict[str, Any]] = []
            while i < len(items) and isinstance(items[i], ToolCall):
                tc: ToolCall = items[i]
                tool_calls_payload.append(
                    {
                        "id": tc.tool_call_id,
                        "type": "function",
                        "function": {
                            "name": tc.tool_name,
                            "arguments": json.dumps(tc.arguments),
                        },
                    }
                )
                i += 1
            result.append({"role": "assistant", "content": None, "tool_calls": tool_calls_payload})

        elif isinstance(item, ToolResult):
            result.append(
                {
                    "role": "tool",
                    "tool_call_id": item.tool_call_id,
                    "content": item.content,
                }
            )
            i += 1

        else:
            #skip
            assert isinstance(item, ErrorItem), f"Unexpected conversation item type: {type(item)}"
            i += 1

    return result


def _build_tools(tools: list[ToolDefinition]) -> list[dict[str, Any]]:
    return [
        ToolDto(
            function=ToolFunctionDto(
                name=tool.name,
                description=tool.description,
                parameters=tool.parameters,
            )
        ).model_dump()
        for tool in tools
    ]
