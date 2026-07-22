from __future__ import annotations

import mcp.types as mcp_types

from app.domain.tools import ToolDefinition, ToolExecutionResult


def to_tool_definition(tool: mcp_types.Tool) -> ToolDefinition:
    return ToolDefinition(
        name=tool.name,
        description=tool.description or "",
        parameters=tool.inputSchema,
    )


def to_tool_execution_result(result: mcp_types.CallToolResult) -> ToolExecutionResult:
    """
    Flatten all TextContent blocks into a single string.
    Non-text blocks (image, audio, resource) are skipped
    """
    parts = [
        block.text
        for block in result.content
        if isinstance(block, mcp_types.TextContent)
    ]
    return ToolExecutionResult(
        content="\n".join(parts) if parts else "",
        is_error=result.isError,
    )
