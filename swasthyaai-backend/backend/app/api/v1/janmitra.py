from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_staff, get_db
from app.core.config import settings
from app.core.rate_limit import limiter
from app.schemas.auth import CurrentStaff
from app.schemas.janmitra import (
    CitizenQueryRequest,
    CitizenQueryResponse,
    EligibilityCheckRequest,
    EligibilityCheckResponse,
    ExtractProfileRequest,
    ExtractProfileResponse,
    SchemeOut,
)
from app.services.janmitra_service import JanMitraService

router = APIRouter(tags=["janmitra"])


@router.get("/schemes", response_model=list[SchemeOut])
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
def list_schemes(request: Request, db: Session = Depends(get_db)) -> list[SchemeOut]:
    return JanMitraService(db).list_schemes()


@router.post("/janmitra/citizen/query", response_model=CitizenQueryResponse)
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
def citizen_query(
    request: Request,
    payload: CitizenQueryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> CitizenQueryResponse:
    return JanMitraService(db).citizen_query(payload.question, payload.language, background_tasks)


@router.post("/janmitra/eligibility/extract", response_model=ExtractProfileResponse)
@limiter.limit(settings.RATE_LIMIT_STAFF)
def extract_profile(
    request: Request,
    payload: ExtractProfileRequest,
    db: Session = Depends(get_db),
    staff: CurrentStaff = Depends(get_current_staff),
) -> ExtractProfileResponse:
    return JanMitraService(db).extract_profile(payload.free_text)


@router.post("/janmitra/eligibility/check", response_model=EligibilityCheckResponse)
@limiter.limit(settings.RATE_LIMIT_STAFF)
def check_eligibility(
    request: Request,
    payload: EligibilityCheckRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    staff: CurrentStaff = Depends(get_current_staff),
) -> EligibilityCheckResponse:
    return JanMitraService(db).check_eligibility(
        payload.profile, payload.phc_id, staff.role, background_tasks
    )
