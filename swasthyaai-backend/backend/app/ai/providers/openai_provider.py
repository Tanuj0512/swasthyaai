import json
from typing import Any, Dict

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.ai.provider_base import AIProvider
from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)

_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise AIProviderError("OPENAI_API_KEY is not configured.")
        self._model = settings.OPENAI_MODEL
        self._client = httpx.Client(
            timeout=settings.AI_REQUEST_TIMEOUT_SECONDS,
            headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
        )

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=6),
        retry=retry_if_exception_type(httpx.TransportError),
    )
    def _call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self._client.post(_URL, json=payload)
        if response.status_code >= 400:
            logger.warning("openai_call_failed", status=response.status_code, body=response.text[:500])
            raise AIProviderError(
                f"OpenAI API returned status {response.status_code}.",
                details={"status": response.status_code},
            )
        return response.json()

    def generate_structured(
        self, *, system_instruction: str, user_prompt: str, json_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        schema_instruction = (
            f"{system_instruction}\n\nRespond ONLY with valid JSON matching this JSON Schema, "
            f"with no markdown fences and no extra text:\n{json.dumps(json_schema)}"
        )
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": schema_instruction},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }
        raw = self._call(payload)
        try:
            content = raw["choices"][0]["message"]["content"]
            return json.loads(content)
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            raise AIProviderError("OpenAI returned a response that was not valid JSON.") from exc

    def generate_text(self, *, system_instruction: str, user_prompt: str) -> str:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
        }
        raw = self._call(payload)
        try:
            return raw["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as exc:
            raise AIProviderError("OpenAI response did not contain expected content.") from exc
