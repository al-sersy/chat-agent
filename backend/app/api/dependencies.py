from __future__ import annotations

from pathlib import Path

from fastapi import Request

from app.application.chat_orchestrator import ChatOrchestrator
from app.config import get_settings
from app.infrastructure.mcp.client import MCPToolClient
from app.infrastructure.openrouter.client import OpenRouterClient


def create_model_client() -> OpenRouterClient:
    """Construct an OpenRouterClient"""
    s = get_settings()
    return OpenRouterClient(
        api_key=s.openrouter_api_key,
        model=s.openrouter_model,
        base_url=s.openrouter_base_url,
        referer=s.openrouter_referer,
    )


def create_mcp_client() -> MCPToolClient:
    """Construct an MCPToolClient."""
    s = get_settings()
    configured_root = Path(s.mcp_filesystem_root)
    if configured_root.is_absolute():
        resolved_root = configured_root
    else:
        repo_root = Path(__file__).resolve().parents[3]
        resolved_root = (repo_root / configured_root).resolve()
    return MCPToolClient(root=resolved_root)


def get_orchestrator(request: Request) -> ChatOrchestrator:
    """FastAPI dependency — returns the shared orchestrator stored on FastAPI app.state"""
    return request.app.state.orchestrator
