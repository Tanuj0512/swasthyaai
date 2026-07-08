"""
Every error the application deliberately raises inherits from AppException.
main.py registers a single exception handler per subclass family so every
error response — regardless of which layer raised it — has the same JSON
shape:

    {
        "error": {
            "code": "NOT_FOUND",
            "message": "PHC 42 was not found.",
            "details": null
        }
    }

This matters for the frontend: it can branch on `error.code` instead of
parsing free-text messages, and it matters for the AI guardrail requirements:
guardrail failures are a distinct, identifiable error family
(GuardrailViolationError), never a generic 500.
"""

from typing import Any, Optional


class AppException(Exception):
    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, details: Optional[Any] = None):
        self.message = message
        self.details = details
        super().__init__(message)


class NotFoundError(AppException):
    status_code = 404
    code = "NOT_FOUND"


class ValidationFailedError(AppException):
    status_code = 422
    code = "VALIDATION_FAILED"


class AuthenticationError(AppException):
    status_code = 401
    code = "AUTHENTICATION_FAILED"


class AuthorizationError(AppException):
    status_code = 403
    code = "NOT_AUTHORIZED"


class ConflictError(AppException):
    status_code = 409
    code = "CONFLICT"


class RuleEngineError(AppException):
    """Raised only for malformed rule configuration — never for a normal
    'not eligible' outcome, which is a valid result, not an error."""

    status_code = 500
    code = "RULE_ENGINE_ERROR"


class AIProviderError(AppException):
    """The configured AI provider (Gemini/OpenAI/Ollama) failed to respond
    or returned something unusable."""

    status_code = 502
    code = "AI_PROVIDER_ERROR"


class GuardrailViolationError(AppException):
    """Raised when input/output guardrail checks (prompt-injection pattern
    match, schema mismatch, ungrounded citation) fail. Always surfaced to the
    client as a safe refusal, never as raw model output."""

    status_code = 422
    code = "GUARDRAIL_VIOLATION"


class ExternalServiceError(AppException):
    """Google STT/TTS, Translation, Maps, or any third-party dependency
    outside our control failed."""

    status_code = 503
    code = "EXTERNAL_SERVICE_ERROR"


class VoiceNotConfiguredError(ExternalServiceError):
    code = "VOICE_NOT_CONFIGURED"
