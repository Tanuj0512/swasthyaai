"""
Ollama runs the configured model locally. Per docs/ARCHITECTURE.md decision
#3, this provider exists for offline local development and testing the AI
Provider abstraction without spending Gemini/OpenAI quota — it is NOT part of
the deployed Cloud Run fallback chain, since Cloud Run's free tier has no
GPU and would cold-start a local model poorly.
"""

import json
from typing import Any, Dict

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.ai.provider_base import AIProvider
from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class OllamaProvider(AIProvider):
    name = "ollama"

    def __init__(self) -> None:
        self._model = settings.OLLAMA_MODEL
        self._client = httpx.Client(base_url=settings.OLLAMA_BASE_URL, timeout=settings.AI_REQUEST_TIMEOUT_SECONDS)

    @retry(
        reraise=True,
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type(httpx.TransportError),
    )
    def _call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = self._client.post("/api/generate", json=payload)
        except httpx.ConnectError as exc:
            raise AIProviderError(
                "Could not reach local Ollama server. Is `ollama serve` running?"
            ) from exc
        if response.status_code >= 400:
            logger.warning("ollama_call_failed", status=response.status_code, body=response.text[:500])
            raise AIProviderError(f"Ollama returned status {response.status_code}.")
        return response.json()

    def generate_structured(
        self, *, system_instruction: str, user_prompt: str, json_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = (
            f"{system_instruction}\n\nRespond ONLY with valid JSON matching this schema, "
            f"no markdown fences, no commentary:\n{json.dumps(json_schema)}\n\n{user_prompt}"
        )
        payload = {"model": self._model, "prompt": prompt, "format": "json", "stream": False}
        raw = self._call(payload)
        try:
            return json.loads(raw["response"])
        except (KeyError, json.JSONDecodeError) as exc:
            raise AIProviderError("Ollama returned a response that was not valid JSON.") from exc

    def generate_text(self, *, system_instruction: str, user_prompt: str) -> str:
        prompt = f"{system_instruction}\n\n{user_prompt}"
        payload = {"model": self._model, "prompt": prompt, "stream": False}
        raw = self._call(payload)
        if "response" not in raw:
            raise AIProviderError("Ollama response did not contain expected content.")
        return raw["response"].strip()
