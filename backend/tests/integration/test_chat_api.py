from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import get_orchestrator
from app.domain.conversation import AssistantMessage, ConversationItem, UserMessage
from app.main import app


class StubOrchestrator:
    async def chat(self, message: str) -> list[ConversationItem]:
        now = datetime.now(timezone.utc)
        return [
            UserMessage(
                type="user_message",
                id=str(uuid.uuid4()),
                timestamp=now,
                content=message,
            ),
            AssistantMessage(
                type="assistant_message",
                id=str(uuid.uuid4()),
                timestamp=now,
                content="Hello from stub!",
            ),
        ]


@pytest.fixture(autouse=True)
def _override(stub: StubOrchestrator) -> None:
    app.dependency_overrides[get_orchestrator] = lambda: stub
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def stub() -> StubOrchestrator:
    return StubOrchestrator()


@pytest.mark.asyncio
async def test_chat_returns_full_conversation() -> None:
    """Valid request returns 200 with items array."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/chat", json={"message": "Hello"})

    assert response.status_code == 200
    data = response.json()
    assert "items" in data

    items = data["items"]
    assert len(items) == 2

    assert items[0]["type"] == "user_message"
    assert items[0]["content"] == "Hello"
    assert "id" in items[0]
    assert "timestamp" in items[0]

    assert items[1]["type"] == "assistant_message"
    assert items[1]["content"] == "Hello from stub!"


@pytest.mark.asyncio
async def test_chat_rejects_missing_message() -> None:
    """Request body without 'message' field returns 422 Unprocessable Entity."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/chat", json={})

    assert response.status_code == 422
