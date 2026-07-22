from __future__ import annotations

import httpx

from app.domain.model import ModelRequest, ModelResponse
from app.infrastructure.openrouter.dto import ChatResponseDto
from app.infrastructure.openrouter.mapper import to_api_payload, to_model_response

_DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
_DEFAULT_REFERER = "http://localhost:5173"


class OpenRouterClient:
    """HTTPX ModelClient communicates with OpenRouter Chat Completions API."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = _DEFAULT_BASE_URL,
        referer: str = _DEFAULT_REFERER,
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url
        self._referer = referer
        self._timeout = timeout

    async def complete(self, request: ModelRequest) -> ModelResponse:
        payload = to_api_payload(request, self._model)

        async with httpx.AsyncClient(timeout=self._timeout) as http:
            response = await http.post(
                f"{self._base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": self._referer,
                },
                json=payload,
            )
            response.raise_for_status()

        validated_dto_response = ChatResponseDto.model_validate(response.json())
        return to_model_response(validated_dto_response)
