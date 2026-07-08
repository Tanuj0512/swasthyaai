"""
Every AI provider (Gemini, OpenAI, Ollama) implements this interface.
Nothing outside `app/ai/` ever imports a provider directly — services call
`app.ai.orchestrator.get_provider()`, which reads `settings.AI_PROVIDER` and
returns the matching implementation. This is the entire mechanism behind
"changing the AI provider should only require changing one configuration."

Design decision — synchronous methods: the rest of this codebase (DB access,
domain logic) is synchronous by design (see app/db/session.py). FastAPI runs
sync route handlers in a threadpool, so a blocking HTTP call here doesn't
block the event loop. Keeping providers synchronous avoids mixing async and
sync code paths through services/repositories, which is a common and
avoidable source of subtle bugs.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class AIProvider(ABC):
    name: str

    @abstractmethod
    def generate_structured(
        self, *, system_instruction: str, user_prompt: str, json_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Return a dict that conforms to `json_schema`. Implementations must
        raise `AIProviderError` (not return partial/invalid data) if the
        underlying model fails to produce valid, schema-conformant JSON."""
        raise NotImplementedError

    @abstractmethod
    def generate_text(self, *, system_instruction: str, user_prompt: str) -> str:
        """Return free-form text for explanation/summarization use cases
        where a fixed schema isn't needed."""
        raise NotImplementedError
