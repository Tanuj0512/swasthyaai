from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.orm import Session

from app.api.v1.deps import enforce_phc_scope, get_current_staff, get_db
from app.core.config import settings
from app.core.rate_limit import limiter
from app.schemas.auth import CurrentStaff
from app.schemas.inventory import (
    ConsumptionLogRequest,
    InventoryForecastResponse,
    InventoryRecommendationResponse,
)
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/{phc_id}/forecast", response_model=InventoryForecastResponse)
@limiter.limit(settings.RATE_LIMIT_STAFF)
def get_forecast(
    request: Request,
    phc_id: int,
    db: Session = Depends(get_db),
    staff: CurrentStaff = Depends(get_current_staff),
) -> InventoryForecastResponse:
    enforce_phc_scope(phc_id, staff)
    return InventoryService(db).get_forecast(phc_id)


@router.get("/{phc_id}/recommendations", response_model=InventoryRecommendationResponse)
@limiter.limit(settings.RATE_LIMIT_STAFF)
def get_recommendations(
    request: Request,
    phc_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    staff: CurrentStaff = Depends(get_current_staff),
) -> InventoryRecommendationResponse:
    enforce_phc_scope(phc_id, staff)
    return InventoryService(db).get_recommendations(phc_id, background_tasks)


@router.post("/{phc_id}/consumption", status_code=204)
@limiter.limit(settings.RATE_LIMIT_STAFF)
def log_consumption(
    request: Request,
    phc_id: int,
    payload: ConsumptionLogRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    staff: CurrentStaff = Depends(get_current_staff),
) -> None:
    enforce_phc_scope(phc_id, staff)
    InventoryService(db).log_consumption(phc_id, payload.medicine_id, payload.quantity_used, background_tasks)
