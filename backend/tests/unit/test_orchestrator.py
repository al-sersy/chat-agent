from __future__ import annotations

import httpx
import pytest

from app.application.chat_orchestrator import (
    ChatOrchestrator,
    _MAX_ITERATIONS,
    _TOOL_RESULT_MAX_CHARS,
)
from app.domain.conversation import AssistantMessage, ErrorItem, ToolCall, ToolResult, UserMessage
from app.domain.model import ModelRequest, ModelResponse, ToolCallParams
from app.domain.tools import ToolDefinition, ToolExecutionResult


# mock implementations 

class MockModelClient:
    """Returns a pre-configured sequence of ModelResponses, one per complete() call."""

    def __init__(self, responses: list[ModelResponse]) -> None:
        self._queue = list(responses)

    async def complete(self, request: ModelRequest) -> ModelResponse:
        return self._queue.pop(0)


class MockToolClient:
    """Returns pre-configured tools and call results."""

    def __init__(
        self,
        tools: list[ToolDefinition] | None = None,
        results: dict[str, ToolExecutionResult] | None = None,
    ) -> None:
        self._tools = tools or []
        self._results = results or {}

    async def list_tools(self) -> list[ToolDefinition]:
        return self._tools

    async def call_tool(self, name: str, arguments: dict[str, object]) -> ToolExecutionResult:
        if name in self._results:
            return self._results[name]
        return ToolExecutionResult(content=f"<result of {name}>")


def _tool_call(tool_call_id: str = "call_1", tool_name: str = "read_file") -> ToolCallParams:
    return ToolCallParams(tool_call_id=tool_call_id, tool_name=tool_name, arguments={})


def _make_orchestrator(responses: list[ModelResponse], **tool_kwargs: object) -> ChatOrchestrator:
    return ChatOrchestrator(MockModelClient(responses), MockToolClient(**tool_kwargs))


@pytest.mark.asyncio
async def test_simple_text_reply() -> None:
    """Model replies with plain text. no tool calls, two items in conversation."""
    orch = _make_orchestrator([ModelResponse(content="Hello!")])

    items = await orch.chat("Hi")

    assert len(items) == 2
    assert isinstance(items[0], UserMessage)
    assert items[0].content == "Hi"
    assert isinstance(items[1], AssistantMessage)
    assert items[1].content == "Hello!"


@pytest.mark.asyncio
async def test_one_tool_call_cycle() -> None:
    """Model makes one tool call then replies. four items in conversation."""
    orch = ChatOrchestrator(
        MockModelClient([
            ModelResponse(tool_calls=[_tool_call("call_1", "read_file")]),
            ModelResponse(content="The file says hello."),
        ]),
        MockToolClient(
            tools=[ToolDefinition("read_file", "Read a file", {"type": "object", "properties": {}})],
            results={"read_file": ToolExecutionResult(content="hello")},
        ),
    )

    items = await orch.chat("Read notes.txt")

    item_types = [type(i).__name__ for i in items]
    assert item_types == ["UserMessage", "ToolCall", "ToolResult", "AssistantMessage"]

    tc: ToolCall = items[1]  # type: ignore[assignment]
    assert tc.tool_call_id == "call_1"
    assert tc.tool_name == "read_file"

    tr: ToolResult = items[2]  # type: ignore[assignment]
    assert tr.tool_call_id == "call_1"
    assert tr.content == "hello"
    assert tr.truncated is False


@pytest.mark.asyncio
async def test_multiple_tool_call_cycles() -> None:
    """Model makes two consecutive tool calls across two iterations."""
    orch = ChatOrchestrator(
        MockModelClient([
            ModelResponse(tool_calls=[_tool_call("c1", "list_directory")]),
            ModelResponse(tool_calls=[_tool_call("c2", "read_file")]),
            ModelResponse(content="Done."),
        ]),
        MockToolClient(
            results={
                "list_directory": ToolExecutionResult(content="notes.txt"),
                "read_file": ToolExecutionResult(content="content"),
            }
        ),
    )

    items = await orch.chat("Explore files")

    item_types = [type(i).__name__ for i in items]
    assert item_types == [
        "UserMessage",
        "ToolCall", "ToolResult",
        "ToolCall", "ToolResult",
        "AssistantMessage",
    ]


@pytest.mark.asyncio
async def test_max_iterations_exceeded() -> None:
    """Model always returns tool calls. orchestrator stops at max iterations."""
    responses = [ModelResponse(tool_calls=[_tool_call()])] * (_MAX_ITERATIONS + 2)
    orch = _make_orchestrator(
        responses,
        results={"read_file": ToolExecutionResult(content="ok")},
    )

    items = await orch.chat("loop forever")

    last = items[-1]
    assert isinstance(last, ErrorItem)
    assert str(_MAX_ITERATIONS) in last.detail


@pytest.mark.asyncio
async def test_model_timeout_appends_error() -> None:
    """httpx.TimeoutException readable in ErrorItem."""

    class TimeoutModel:
        async def complete(self, request: ModelRequest) -> ModelResponse:
            raise httpx.TimeoutException("read timeout")

    orch = ChatOrchestrator(TimeoutModel(), MockToolClient())
    items = await orch.chat("hello")

    last = items[-1]
    assert isinstance(last, ErrorItem)
    assert "timed out" in last.detail.lower() or "long" in last.detail.lower()


@pytest.mark.asyncio
async def test_model_http_error_appends_error() -> None:
    """httpx.HTTPStatusError readable in ErrorItem."""

    class HttpErrorModel:
        async def complete(self, request: ModelRequest) -> ModelResponse:
            response = httpx.Response(status_code=429, request=httpx.Request("POST", "http://x"))
            raise httpx.HTTPStatusError("rate limited", request=response.request, response=response)

    orch = ChatOrchestrator(HttpErrorModel(), MockToolClient())
    items = await orch.chat("hello")

    last = items[-1]
    assert isinstance(last, ErrorItem)
    assert "429" in last.detail


@pytest.mark.asyncio
async def test_tool_execution_error_appends_error() -> None:
    """Exception from call_tool readable in ErrorItem."""

    class BrokenToolClient:
        async def list_tools(self) -> list[ToolDefinition]:
            return [ToolDefinition("boom", "Explodes", {"type": "object", "properties": {}})]

        async def call_tool(self, name: str, arguments: dict[str, object]) -> ToolExecutionResult:
            raise RuntimeError("disk error")

    orch = ChatOrchestrator(
        MockModelClient([ModelResponse(tool_calls=[_tool_call("c1", "boom")])]),
        BrokenToolClient(),
    )
    items = await orch.chat("break something")

    last = items[-1]
    assert isinstance(last, ErrorItem)
    assert "boom" in last.detail


@pytest.mark.asyncio
async def test_tool_result_truncation() -> None:
    """Tool result longer than the limit is truncated and truncated=True."""
    big = "x" * (_TOOL_RESULT_MAX_CHARS + 500)
    orch = ChatOrchestrator(
        MockModelClient([
            ModelResponse(tool_calls=[_tool_call()]),
            ModelResponse(content="done"),
        ]),
        MockToolClient(results={"read_file": ToolExecutionResult(content=big)}),
    )

    items = await orch.chat("read big file")

    tr: ToolResult = next(i for i in items if isinstance(i, ToolResult))
    assert tr.truncated is True
    assert "truncated" in tr.content.lower()
    assert len(tr.content) < len(big)


@pytest.mark.asyncio
async def test_conversation_accumulates_across_turns() -> None:
    """Each call to chat() appends to the same conversation history."""
    orch = _make_orchestrator([
        ModelResponse(content="Hi there!"),
        ModelResponse(content="Doing well."),
    ])

    first = await orch.chat("Hello")
    assert len(first) == 2

    second = await orch.chat("How are you?")
    assert len(second) == 4  # 2 previous + UserMessage + AssistantMessage
    assert isinstance(second[2], UserMessage)
    assert second[2].content == "How are you?"
