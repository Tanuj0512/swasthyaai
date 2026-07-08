from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.v1.deps import enforce_phc_scope, get_current_staff, get_db
from app.core.config import settings
from app.core.rate_limit import limiter
from app.schemas.auth import CurrentStaff
from app.schemas.dashboard import DashboardSnapshot, PHCOut
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/phcs", tags=["dashboard"])


@router.get("", response_model=list[PHCOut])
@limiter.limit(settings.RATE_LIMIT_PUBLIC)
def list_phcs(request: Request, db: Session = Depends(get_db)) -> list[PHCOut]:
    return DashboardService(db).list_phcs()


@router.get("/{phc_id}/dashboard", response_model=DashboardSnapshot)
@limiter.limit(settings.RATE_LIMIT_STAFF)
def get_dashboard(
    request: Request,
    phc_id: int,
    db: Session = Depends(get_db),
    staff: CurrentStaff = Depends(get_current_staff),
) -> DashboardSnapshot:
    enforce_phc_scope(phc_id, staff)
    return DashboardService(db).get_dashboard(phc_id)
