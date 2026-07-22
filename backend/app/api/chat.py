from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_orchestrator
from app.application.chat_orchestrator import ChatOrchestrator

router = APIRouter(prefix="/api")


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(
    body: ChatRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
) -> dict:
    """
    POST /api/chat
    Request:  { "message": string }
    Response: { "items": ConversationItem[] }  — full conversation, not delta
    """
    items = await orchestrator.chat(body.message)
    return {"items": [item.model_dump(mode="json") for item in items]}
