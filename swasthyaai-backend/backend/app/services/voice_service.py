from typing import Literal, Optional

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ExternalServiceError, VoiceNotConfiguredError
from app.core.logging import get_logger
from app.schemas.common import AIExplanation
from app.schemas.voice import VoiceQueryResponse
from app.services.inventory_service import InventoryService
from app.services.janmitra_service import JanMitraService

logger = get_logger(__name__)

_LANGUAGE_CODE_MAP = {"en": "en-IN", "hi": "hi-IN"}


def _require_voice_configured() -> None:
    if not settings.GOOGLE_APPLICATION_CREDENTIALS:
        raise VoiceNotConfiguredError(
            "Voice features are not configured on this deployment. "
            "Set GOOGLE_APPLICATION_CREDENTIALS to enable Module 5."
        )


def _transcribe(audio_bytes: bytes, language: str) -> str:
    _require_voice_configured()
    try:
        from google.cloud import speech
    except ImportError as exc:  # pragma: no cover - import guarded for environments without the package
        raise VoiceNotConfiguredError("google-cloud-speech is not installed.") from exc

    try:
        client = speech.SpeechClient()
        audio = speech.RecognitionAudio(content=audio_bytes)
        # Browsers' MediaRecorder API produces WebM/Opus (Chrome, Edge,
        # Firefox) — there is no straightforward client-side path to raw
        # LINEAR16 PCM without an audio worklet, so the backend is
        # configured to accept the container the frontend actually
        # produces rather than pushing that complexity onto the client.
        # Sample rate is intentionally omitted: it's embedded in the WebM
        # container itself, and Google recommends not overriding it.
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            language_code=_LANGUAGE_CODE_MAP.get(language, "en-IN"),
        )
        response = client.recognize(config=config, audio=audio)
    except Exception as exc:  # noqa: BLE001
        logger.error("stt_call_failed", exc_info=True)
        raise ExternalServiceError("Speech-to-text service failed to process the audio.") from exc

    if not response.results:
        raise ExternalServiceError("Could not transcribe any speech from the provided audio.")

    return response.results[0].alternatives[0].transcript


def _synthesize(text: str, language: str) -> bytes:
    _require_voice_configured()
    try:
        from google.cloud import texttospeech
    except ImportError as exc:  # pragma: no cover
        raise VoiceNotConfiguredError("google-cloud-texttospeech is not installed.") from exc

    try:
        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=_LANGUAGE_CODE_MAP.get(language, "en-IN"),
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    except Exception as exc:  # noqa: BLE001
        logger.error("tts_call_failed", exc_info=True)
        raise ExternalServiceError("Text-to-speech service failed to synthesize audio.") from exc

    return response.audio_content


class VoiceService:
    def __init__(self, db: Session):
        self.db = db
        self.janmitra_service = JanMitraService(db)
        self.inventory_service = InventoryService(db)

    def handle_voice_query(
        self,
        audio_bytes: bytes,
        language: Literal["en", "hi"],
        mode: Literal["citizen_scheme_query", "inventory_query"],
        phc_id: Optional[int],
        background_tasks: BackgroundTasks,
    ) -> VoiceQueryResponse:
        transcript = _transcribe(audio_bytes, language)

        if mode == "citizen_scheme_query":
            result = self.janmitra_service.citizen_query(transcript, language, background_tasks)
            explanation = result.explanation
        else:
            if phc_id is None:
                raise ExternalServiceError("phc_id is required for inventory_query voice mode.")
            result = self.inventory_service.get_recommendations(phc_id, background_tasks)
            explanation = result.explanation

        audio_content = _synthesize(explanation.text, language)
        import base64

        return VoiceQueryResponse(
            transcript=transcript,
            detected_language=language,
            matched_mode=mode,
            explanation=AIExplanation(text=explanation.text, provider=explanation.provider, grounded=explanation.grounded),
            audio_base64=base64.b64encode(audio_content).decode("ascii"),
            audio_content_type="audio/mpeg",
        )
