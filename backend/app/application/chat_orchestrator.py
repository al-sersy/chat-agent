from __future__ import annotations

import uuid
from datetime import datetime, timezone

import httpx

from app.domain.conversation import (
    AssistantMessage,
    ConversationItem,
    ErrorItem,
    ToolCall,
    ToolResult,
    UserMessage,
)
from app.domain.model import ModelClient, ModelRequest
from app.domain.tools import ToolClient

_MAX_ITERATIONS = 8
_TOOL_RESULT_MAX_CHARS = 20_000


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return str(uuid.uuid4())


class ChatOrchestrator:
    """
    Core agentic loop 

    """

    def __init__(self, model_client: ModelClient, tool_client: ToolClient) -> None:
        self._model = model_client
        self._tools = tool_client
        self._conversation: list[ConversationItem] = []

    async def chat(self, user_message: str) -> list[ConversationItem]:
        """
        Append the user message, run the agentic loop, and return the full
        conversation history (including all prior turns).
        """
        # chat journey 1 — append UserMessage
        self._conversation.append(
            UserMessage(
                type="user_message",
                id=_new_id(),
                timestamp=_now(),
                content=user_message,
            )
        )

        for _iteration in range(_MAX_ITERATIONS):

            # chat journey 2 — call the model with full history + current tools
            try:
                tools = await self._tools.list_tools()
                response = await self._model.complete(
                    ModelRequest(messages=list(self._conversation), tools=tools)
                )
            except httpx.TimeoutException:
                return self._append_error("The model took too long to respond. Please try again.")
            except httpx.HTTPStatusError as exc:
                return self._append_error(
                    f"The model returned HTTP {exc.response.status_code}. Please try again."
                )
            except Exception:
                return self._append_error(
                    "An unexpected error occurred while contacting the model."
                )

            # chat journey 3 — handle tool calls
            if response.tool_calls:
                for tc in response.tool_calls:
                    # chat journey — append tool call
                    self._conversation.append(
                        ToolCall(
                            type="tool_call",
                            id=_new_id(),
                            timestamp=_now(),
                            tool_call_id=tc.tool_call_id,
                            tool_name=tc.tool_name,
                            arguments=tc.arguments,
                        )
                    )

                    # chat journey — execute the tool
                    try:
                        exec_result = await self._tools.call_tool(tc.tool_name, tc.arguments)
                    except Exception:
                        return self._append_error(
                            f"Tool '{tc.tool_name}' could not be executed."
                        )

                    # chat journey — bound result size
                    content = exec_result.content
                    truncated = False
                    if len(content) > _TOOL_RESULT_MAX_CHARS:
                        content = (
                            content[:_TOOL_RESULT_MAX_CHARS]
                            + "\n[truncated — output exceeded 20,000 chars]"
                        )
                        truncated = True

                    # chat journey — record the tool result to chat history
                    self._conversation.append(
                        ToolResult(
                            type="tool_result",
                            id=_new_id(),
                            timestamp=_now(),
                            tool_call_id=tc.tool_call_id,
                            content=content,
                            truncated=truncated,
                        )
                    )

                # chat journey  — go to chat journey 2 "back to next iteration"
                continue

            # chat journey 4 — no tool calls: final assistant reply
            self._conversation.append(
                AssistantMessage(
                    type="assistant_message",
                    id=_new_id(),
                    timestamp=_now(),
                    content=response.content or "",
                )
            )
            return list(self._conversation)

        return self._append_error(
            f"The agent reached the maximum of {_MAX_ITERATIONS} iterations "
            "without producing a final answer."
        )


    async def chat_stream(self, user_message: str):
        """Yield each conversation item as it is produced, for SSE streaming."""
        user_msg = UserMessage(
            type="user_message",
            id=_new_id(),
            timestamp=_now(),
            content=user_message,
        )
        self._conversation.append(user_msg)
        yield user_msg

        for _iteration in range(_MAX_ITERATIONS):
            try:
                tools = await self._tools.list_tools()
                response = await self._model.complete(
                    ModelRequest(messages=list(self._conversation), tools=tools)
                )
            except httpx.TimeoutException:
                item = self._make_error("The model took too long to respond. Please try again.")
                self._conversation.append(item)
                yield item
                return
            except httpx.HTTPStatusError as exc:
                item = self._make_error(
                    f"The model returned HTTP {exc.response.status_code}. Please try again."
                )
                self._conversation.append(item)
                yield item
                return
            except Exception:
                item = self._make_error("An unexpected error occurred while contacting the model.")
                self._conversation.append(item)
                yield item
                return

            if response.tool_calls:
                for tc in response.tool_calls:
                    tool_call = ToolCall(
                        type="tool_call",
                        id=_new_id(),
                        timestamp=_now(),
                        tool_call_id=tc.tool_call_id,
                        tool_name=tc.tool_name,
                        arguments=tc.arguments,
                    )
                    self._conversation.append(tool_call)
                    yield tool_call

                    try:
                        exec_result = await self._tools.call_tool(tc.tool_name, tc.arguments)
                    except Exception:
                        item = self._make_error(f"Tool '{tc.tool_name}' could not be executed.")
                        self._conversation.append(item)
                        yield item
                        return

                    content = exec_result.content
                    truncated = False
                    if len(content) > _TOOL_RESULT_MAX_CHARS:
                        content = (
                            content[:_TOOL_RESULT_MAX_CHARS]
                            + "\n[truncated — output exceeded 20,000 chars]"
                        )
                        truncated = True

                    tool_result = ToolResult(
                        type="tool_result",
                        id=_new_id(),
                        timestamp=_now(),
                        tool_call_id=tc.tool_call_id,
                        content=content,
                        truncated=truncated,
                    )
                    self._conversation.append(tool_result)
                    yield tool_result

                continue

            assistant_msg = AssistantMessage(
                type="assistant_message",
                id=_new_id(),
                timestamp=_now(),
                content=response.content or "",
            )
            self._conversation.append(assistant_msg)
            yield assistant_msg
            return

        item = self._make_error(
            f"The agent reached the maximum of {_MAX_ITERATIONS} iterations "
            "without producing a final answer."
        )
        self._conversation.append(item)
        yield item

    def _make_error(self, detail: str) -> ErrorItem:
        return ErrorItem(type="error", id=_new_id(), timestamp=_now(), detail=detail)

    def _append_error(self, detail: str) -> list[ConversationItem]:
        self._conversation.append(self._make_error(detail))
        return list(self._conversation)
