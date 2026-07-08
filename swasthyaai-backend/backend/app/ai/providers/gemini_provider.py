import json
from typing import Any, Dict

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.ai.provider_base import AIProvider
from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)

_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            raise AIProviderError("GEMINI_API_KEY is not configured.")
        self._model = settings.GEMINI_MODEL
        self._api_key = settings.GEMINI_API_KEY
        self._client = httpx.Client(timeout=settings.AI_REQUEST_TIMEOUT_SECONDS)

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=6),
        retry=retry_if_exception_type(httpx.TransportError),
    )
    def _call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{_BASE_URL}/{self._model}:generateContent?key={self._api_key}"
        response = self._client.post(url, json=payload)
        if response.status_code >= 400:
            logger.warning("gemini_call_failed", status=response.status_code, body=response.text[:500])
            raise AIProviderError(
                f"Gemini API returned status {response.status_code}.",
                details={"status": response.status_code},
            )
        return response.json()

    def _extract_text(self, response_json: Dict[str, Any]) -> str:
        try:
            candidates = response_json["candidates"]
            parts = candidates[0]["content"]["parts"]
            return "".join(part.get("text", "") for part in parts)
        except (KeyError, IndexError) as exc:
            raise AIProviderError("Gemini response did not contain expected content.") from exc

    def generate_structured(
        self, *, system_instruction: str, user_prompt: str, json_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": json_schema,
                "temperature": 0.1,
            },
        }
        raw = self._call(payload)
        text = self._extract_text(raw)
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise AIProviderError("Gemini returned malformed JSON.", details={"raw": text[:300]}) from exc

    def generate_text(self, *, system_instruction: str, user_prompt: str) -> str:
        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": 0.3},
        }
        raw = self._call(payload)
        return self._extract_text(raw).strip()
