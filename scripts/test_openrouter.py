"""
Throwaway verification script — Phase 2.

Run from the repo root after setting up your .env:

    cd backend
    python ../scripts/test_openrouter.py

Expected output when tool-calling works:
    Got 1 tool call(s):
      Tool: get_weather | Args: {'city': 'Paris'} | ID: call_...

If you see a plain text response instead, the model doesn't support tool calling
— pick a different model in .env (OPENROUTER_MODEL).
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path
import uuid

# Allow running without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.config import get_settings
from app.domain.conversation import UserMessage
from app.domain.model import ModelRequest
from app.domain.tools import ToolDefinition
from app.infrastructure.openrouter.client import OpenRouterClient


async def main() -> None:
    settings = get_settings()
    client = OpenRouterClient(
        api_key=settings.openrouter_api_key,
        model=settings.openrouter_model,
        base_url=settings.openrouter_base_url,
        referer=settings.openrouter_referer,
    )

    fake_tool = ToolDefinition(
        name="get_weather",
        description="Get the current weather for a given city.",
        parameters={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city name"},
            },
            "required": ["city"],
        },
    )

    user_msg = UserMessage(
        type="user_message",
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        content="What's the weather in Paris right now? Use the get_weather tool.",
    )

    print(f"Model : {settings.openrouter_model}")
    print(f"Prompt: {user_msg.content}\n")

    request = ModelRequest(messages=[user_msg], tools=[fake_tool])
    response = await client.complete(request)

    if response.tool_calls:
        print(f"Got {len(response.tool_calls)} tool call(s):")
        for tc in response.tool_calls:
            print(f"  Tool: {tc.tool_name} | ID: {tc.tool_call_id} | Args: {tc.arguments} ")
    else:
        print(f"Got text response (no tool call — model may not support tools):\n{response.content}")


if __name__ == "__main__":
    asyncio.run(main())
