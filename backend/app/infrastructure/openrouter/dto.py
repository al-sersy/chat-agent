from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


# request

class ToolFunctionDto(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema


class ToolDto(BaseModel):
    type: Literal["function"] = "function"
    function: ToolFunctionDto


# response

class ToolCallFunctionDto(BaseModel):
    name: str
    arguments: str  # JSON-encoded string


class ToolCallItemDto(BaseModel):
    id: str
    type: Literal["function"] = "function"
    function: ToolCallFunctionDto


class AssistantRespDto(BaseModel):
    role: str
    content: str | None = None
    tool_calls: list[ToolCallItemDto] | None = None


class ChoiceDto(BaseModel):
    message: AssistantRespDto
    finish_reason: str | None = None


class ChatResponseDto(BaseModel):
    choices: list[ChoiceDto] = Field(min_length=1)
