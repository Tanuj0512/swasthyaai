from typing import Literal

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session

from app.api.v1.deps import enforce_phc_scope, get_current_staff, get_db
from app.core.config import settings
from app.core.rate_limit import limiter
from app.schemas.auth import CurrentStaff
from app.schemas.voice import VoiceQueryResponse
from app.services.voice_service import VoiceService

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/citizen-query", response_model=VoiceQueryResponse)
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
async def voice_citizen_query(
    request: Request,
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    language: Literal["en", "hi"] = Form("en"),
    db: Session = Depends(get_db),
) -> VoiceQueryResponse:
    audio_bytes = await audio.read()
    return VoiceService(db).handle_voice_query(
        audio_bytes, language, "citizen_scheme_query", phc_id=None, background_tasks=background_tasks
    )


@router.post("/inventory-query/{phc_id}", response_model=VoiceQueryResponse)
@limiter.limit(settings.RATE_LIMIT_STAFF)
async def voice_inventory_query(
    request: Request,
    phc_id: int,
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    language: Literal["en", "hi"] = Form("en"),
    db: Session = Depends(get_db),
    staff: CurrentStaff = Depends(get_current_staff),
) -> VoiceQueryResponse:
    enforce_phc_scope(phc_id, staff)
    audio_bytes = await audio.read()
    return VoiceService(db).handle_voice_query(
        audio_bytes, language, "inventory_query", phc_id=phc_id, background_tasks=background_tasks
    )
