from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class UserMessage(BaseModel):
    type: Literal["user_message"]
    id: str
    timestamp: datetime
    content: str


class AssistantMessage(BaseModel):
    type: Literal["assistant_message"]
    id: str
    timestamp: datetime
    content: str


class ToolCall(BaseModel):
    type: Literal["tool_call"]
    id: str
    timestamp: datetime
    tool_call_id: str
    tool_name: str
    arguments: dict[str, object]


class ToolResult(BaseModel):
    type: Literal["tool_result"]
    id: str
    timestamp: datetime
    tool_call_id: str
    content: str
    truncated: bool = False


class ErrorItem(BaseModel):
    type: Literal["error"]
    id: str
    timestamp: datetime
    detail: str


ConversationItem = Annotated[
    UserMessage | AssistantMessage | ToolCall | ToolResult | ErrorItem,
    Field(discriminator="type"),
]
