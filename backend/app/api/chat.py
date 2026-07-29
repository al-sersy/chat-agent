from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
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


@router.post("/chat/stream")
async def chat_stream(
    body: ChatRequest,
    orchestrator: ChatOrchestrator = Depends(get_orchestrator),
) -> StreamingResponse:
    async def event_generator():
        async for item in orchestrator.chat_stream(body.message):
            yield f"data: {item.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
