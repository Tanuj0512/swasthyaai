from typing import Any, Optional

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class AIExplanation(BaseModel):
    """Every AI-generated explanation returned by the API carries this
    envelope so the frontend can always show provenance and never mistake an
    AI explanation for a raw database fact."""

    text: str
    provider: str
    grounded: bool
    disclaimer: str = "AI-generated explanation. Verify critical details with PHC staff."
