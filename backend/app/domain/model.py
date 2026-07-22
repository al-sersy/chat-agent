from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .conversation import ConversationItem
    from .tools import ToolDefinition


@dataclass
class ToolCallParams:
    """A single tool call requested by the model in its response."""
    tool_call_id: str
    tool_name: str
    arguments: dict[str, object]


@dataclass
class ModelRequest:
    """Everything the model needs: full conversation history + available tools."""
    messages: list[ConversationItem]
    tools: list[ToolDefinition]


@dataclass
class ModelResponse:
    """What the model returned: either a text reply or one-or-more tool calls."""
    content: str | None = None
    tool_calls: list[ToolCallParams] = field(default_factory=list)


class ModelClient(Protocol):
    async def complete(self, request: ModelRequest) -> ModelResponse: ...
