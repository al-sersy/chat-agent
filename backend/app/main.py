from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.dependencies import create_mcp_client, create_model_client
from app.application.chat_orchestrator import ChatOrchestrator
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    mcp_client = create_mcp_client()
    model_client = create_model_client()
    app.state.orchestrator = ChatOrchestrator(model_client, mcp_client)
    await mcp_client.start()
    try:
        yield
    finally:
        await mcp_client.stop()


app = FastAPI(title="ChatAgent API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().cors_origin],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(chat_router)
