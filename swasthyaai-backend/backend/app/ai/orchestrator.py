"""
Two responsibilities live here:

1. `get_provider()` — the factory that reads `settings.AI_PROVIDER` and
   returns the matching `AIProvider` implementation. This is the entire
   mechanism behind swapping Gemini/OpenAI/Ollama via one env var.

2. `AIOrchestrator` — the single place every service goes through to talk to
   an AI provider. It applies the shared system-prompt guardrail wrapper,
   verifies explanation output is grounded in the facts it was given, and —
   critically — degrades gracefully: if the provider is unreachable or
   unconfigured, explanation calls fall back to a deterministic templated
   explanation instead of returning a 500 to the end user. Extraction calls
   (turning free text into a structured profile) cannot sensibly fall back
   to a template, so those propagate the error to the caller.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.ai.guardrails import build_system_instruction, verify_grounded
from app.ai.provider_base import AIProvider
from app.core.config import settings
from app.core.exceptions import AIProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


def get_provider() -> AIProvider:
    provider_name = settings.AI_PROVIDER
    if provider_name == "gemini":
        from app.ai.providers.gemini_provider import GeminiProvider

        return GeminiProvider()
    if provider_name == "openai":
        from app.ai.providers.openai_provider import OpenAIProvider

        return OpenAIProvider()
    if provider_name == "ollama":
        from app.ai.providers.ollama_provider import OllamaProvider

        return OllamaProvider()
    raise AIProviderError(f"Unknown AI_PROVIDER '{provider_name}' configured.")


@dataclass
class ExplanationResult:
    text: str
    provider: str
    grounded: bool
    succeeded: bool
    guardrail_flags: Dict[str, Any] = field(default_factory=dict)


class AIOrchestrator:
    def __init__(self, provider: Optional[AIProvider] = None):
        self._provider = provider

    def _resolve_provider(self) -> AIProvider:
        if self._provider is not None:
            return self._provider
        return get_provider()

    def get_active_provider_name(self) -> str:
        """Public accessor for callers that just need to report which
        provider is configured (e.g. attaching it to a non-explanation
        response) without triggering a generation call."""
        return self._resolve_provider().name

    def generate_grounded_explanation(
        self,
        *,
        system_instruction_base: str,
        user_prompt: str,
        grounding_terms: List[str],
        fallback_text: str,
    ) -> ExplanationResult:
        try:
            provider = self._resolve_provider()
        except AIProviderError as exc:
            logger.info("ai_provider_unavailable_using_fallback", error=str(exc))
            return ExplanationResult(
                text=fallback_text,
                provider="fallback_template",
                grounded=True,
                succeeded=False,
                guardrail_flags={"reason": "provider_unavailable"},
            )

        system_instruction = build_system_instruction(system_instruction_base)
        try:
            text = provider.generate_text(system_instruction=system_instruction, user_prompt=user_prompt)
        except AIProviderError as exc:
            logger.warning("ai_generation_failed_using_fallback", error=str(exc), provider=provider.name)
            return ExplanationResult(
                text=fallback_text,
                provider="fallback_template",
                grounded=True,
                succeeded=False,
                guardrail_flags={"reason": "generation_failed"},
            )

        if not verify_grounded(text, grounding_terms):
            logger.warning("ai_output_failed_grounding_check_using_fallback", provider=provider.name)
            return ExplanationResult(
                text=fallback_text,
                provider="fallback_template",
                grounded=True,
                succeeded=False,
                guardrail_flags={"reason": "grounding_check_failed"},
            )

        return ExplanationResult(text=text, provider=provider.name, grounded=True, succeeded=True)

    def extract_structured(
        self,
        *,
        system_instruction_base: str,
        user_prompt: str,
        json_schema: Dict[str, Any],
    ) -> Dict[str, Any]:
        """No fallback here by design — a structured extraction that failed
        must surface as an error so the caller (and the user) knows the
        profile was NOT reliably extracted, rather than silently proceeding
        with empty/default field values."""
        provider = self._resolve_provider()
        system_instruction = build_system_instruction(system_instruction_base)
        return provider.generate_structured(
            system_instruction=system_instruction, user_prompt=user_prompt, json_schema=json_schema
        )
