from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.deps import get_db
from app.core.exceptions import ExternalServiceError

router = APIRouter(tags=["health"])


@router.get("/health")
def liveness() -> dict:
    return {"status": "ok"}


@router.get("/health/db")
def readiness(db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        raise ExternalServiceError("Database is not reachable.") from exc
    return {"status": "ok", "database": "reachable"}
