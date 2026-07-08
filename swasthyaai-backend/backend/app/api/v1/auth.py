from fastapi import APIRouter, Depends, Request

from app.api.v1.deps import get_current_staff
from app.core.config import settings
from app.core.rate_limit import limiter
from app.schemas.auth import CurrentStaff

router = APIRouter(prefix="/staff", tags=["auth"])


@router.get("/me", response_model=CurrentStaff)
@limiter.limit(settings.RATE_LIMIT_STAFF)
def get_me(request: Request, staff: CurrentStaff = Depends(get_current_staff)) -> CurrentStaff:
    """
    The frontend calls this immediately after a Supabase login to learn the
    caller's role and PHC/district scope — there is no other way to derive
    this client-side, since the JWT itself only proves identity, not role.
    """
    return staff
