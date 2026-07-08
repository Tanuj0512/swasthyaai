from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db, require_role
from app.core.config import settings
from app.core.rate_limit import limiter
from app.models.staff import StaffRole
from app.schemas.auth import CurrentStaff
from app.schemas.district import CopilotQueryRequest, CopilotQueryResponse, DistrictOut, DistrictSummaryResponse
from app.services.district_service import DistrictService

router = APIRouter(prefix="/district", tags=["district"])

_district_or_admin = require_role(StaffRole.DISTRICT_OFFICER, StaffRole.ADMIN)


@router.get("", response_model=list[DistrictOut])
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
def list_districts(request: Request, db: Session = Depends(get_db)) -> list[DistrictOut]:
    return DistrictService(db).list_districts()


@router.get("/{district_id}/summary", response_model=DistrictSummaryResponse)
@limiter.limit(settings.RATE_LIMIT_STAFF)
def get_summary(
    request: Request,
    district_id: int,
    db: Session = Depends(get_db),
    staff: CurrentStaff = Depends(_district_or_admin),
) -> DistrictSummaryResponse:
    return DistrictService(db).get_district_summary(district_id)


@router.post("/{district_id}/copilot/query", response_model=CopilotQueryResponse)
@limiter.limit(settings.RATE_LIMIT_STAFF)
def copilot_query(
    request: Request,
    district_id: int,
    payload: CopilotQueryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    staff: CurrentStaff = Depends(_district_or_admin),
) -> CopilotQueryResponse:
    return DistrictService(db).answer_copilot_query(district_id, payload.question, background_tasks)
