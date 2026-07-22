from __future__ import annotations

import contextlib
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from app.domain.tools import ToolDefinition, ToolExecutionResult
from app.infrastructure.mcp.mapper import to_tool_definition, to_tool_execution_result


def _server_params(root: str | Path) -> StdioServerParameters:
    """Build params config for MCP server"""
    absolute_path = str(Path(root).resolve())
    return StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", absolute_path],
    )


class MCPToolClient:
    """
    ToolClient backed by the MCP server over stdio.

    Lifecycle — use one of:
      async with MCPToolClient(root) as client: ...
      client = MCPToolClient(root); await client.start(); ...; await client.stop()
    """

    def __init__(self, root: str | Path) -> None:
        self._params = _server_params(root)
        self._session: ClientSession | None = None
        self._stack = contextlib.AsyncExitStack()

    async def start(self) -> None:
        """
        Spawn the MCP server process, open the session, and call initialize().
        Raises RuntimeError immediately if the server won't connect (fail-fast).
        """
        try:
            read, write = await self._stack.enter_async_context(stdio_client(self._params))
            session = await self._stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            self._session = session
        except Exception as exc:
            await self.stop()
            raise RuntimeError(f"MCP filesystem server failed to connect: {exc}") from exc

    async def stop(self) -> None:
        """Close the MCP session and terminate the stdio process."""
        await self._stack.aclose()
        self._session = None

    async def __aenter__(self) -> MCPToolClient:
        await self.start()
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.stop()

    # ToolClient protocol

    async def list_tools(self) -> list[ToolDefinition]:
        session = self._assert_started()
        result = await session.list_tools()
        return [to_tool_definition(tool) for tool in result.tools]

    async def call_tool(self, name: str, arguments: dict[str, object]) -> ToolExecutionResult:
        session = self._assert_started()
        result = await session.call_tool(name, arguments)
        return to_tool_execution_result(result)

    def _assert_started(self) -> ClientSession:
        if self._session is None:
            raise RuntimeError("MCPToolClient not started — call start().")
        return self._session