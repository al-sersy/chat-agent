from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class ToolDefinition:
    """Describes a single tool the model can invoke."""
    name: str
    description: str
    parameters: dict[str, Any]


@dataclass
class ToolExecutionResult:
    """Raw result of calling a tool via the MCP client."""
    content: str
    is_error: bool = False


class ToolClient(Protocol):
    async def list_tools(self) -> list[ToolDefinition]: ...
    async def call_tool(self, name: str, arguments: dict[str, object]) -> ToolExecutionResult: ...
