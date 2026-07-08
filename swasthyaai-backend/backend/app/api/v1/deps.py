from typing import Callable, Optional

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_supabase_jwt
from app.db.session import get_db
from app.models.staff import StaffRole
from app.repositories.staff_repository import StaffRepository
from app.schemas.auth import CurrentStaff

__all__ = ["get_db", "get_current_staff", "require_role", "enforce_phc_scope"]


def _extract_bearer_token(authorization: Optional[str]) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthenticationError("Missing or malformed Authorization header.")
    return authorization.split(" ", 1)[1].strip()


# def get_current_staff(
#     authorization: Optional[str] = Header(default=None),
#     db: Session = Depends(get_db),
# ) -> CurrentStaff:
#     """
#     Verifies the Supabase JWT, then loads the corresponding `staff_profiles`
#     row. A valid token with no matching staff profile is still a 401 (not a
#     403) — from the API's point of view, an unrecognized identity is
#     unauthenticated, since it has no application-level identity yet.
#     """
#     token = _extract_bearer_token(authorization)
#     payload = decode_supabase_jwt(token)
#     user_id = payload["sub"]

#     staff_repo = StaffRepository(db)
#     staff = staff_repo.get(user_id)
#     if staff is None:
#         raise AuthenticationError("No staff profile is associated with this account.")

#     return CurrentStaff.model_validate(staff)
def get_current_staff(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> CurrentStaff:
    # --- TEMP DEBUG: bypass auth, remove before committing ---
    import os
    if os.getenv("DEBUG_SKIP_AUTH") == "1":
        staff_repo = StaffRepository(db)
        staff = staff_repo.get("<a real user_id from staff_profiles table>")
        if staff:
            return CurrentStaff.model_validate(staff)
    # --- end temp debug ---

    token = _extract_bearer_token(authorization)
    payload = decode_supabase_jwt(token)
    user_id = payload["sub"]

    staff_repo = StaffRepository(db)
    staff = staff_repo.get(user_id)
    if staff is None:
        raise AuthenticationError("No staff profile is associated with this account.")

    return CurrentStaff.model_validate(staff)

def require_role(*roles: StaffRole) -> Callable[[CurrentStaff], CurrentStaff]:
    allowed = {r.value for r in roles}

    def _dependency(staff: CurrentStaff = Depends(get_current_staff)) -> CurrentStaff:
        if staff.role not in allowed:
            raise AuthorizationError(f"This action requires one of roles: {sorted(allowed)}.")
        return staff

    return _dependency


def enforce_phc_scope(phc_id: int, staff: CurrentStaff) -> None:
    """
    PHC staff may only act on their own PHC. District officers and admins are
    not restricted here (their access to a PHC's data is a read-only
    aggregate handled at the district level, not this per-PHC write path).
    This is an additional application-layer check on top of the database's
    own Row-Level-Security policies — defense in depth, not a replacement
    for RLS.
    """
    if staff.role == StaffRole.PHC_STAFF.value and staff.phc_id != phc_id:
        raise AuthorizationError("You are not authorized to access this PHC's data.")
