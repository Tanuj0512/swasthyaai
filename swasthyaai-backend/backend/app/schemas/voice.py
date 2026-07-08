from typing import Literal, Optional

from pydantic import BaseModel

from app.schemas.common import AIExplanation


class VoiceQueryResponse(BaseModel):
    transcript: str
    detected_language: str
    matched_mode: Literal["citizen_scheme_query", "inventory_query"]
    explanation: AIExplanation
    audio_base64: Optional[str] = None
    audio_content_type: str = "audio/mpeg"
