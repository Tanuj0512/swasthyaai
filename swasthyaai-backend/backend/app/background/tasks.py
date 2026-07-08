"""
FastAPI `BackgroundTasks` run after the response has been sent, in the same
process. Each task here opens and closes its own DB session rather than
reusing the request's session (which FastAPI has already closed by the time
a background task runs) — this is a common and easy-to-miss correctness bug
in FastAPI apps, so every function below is self-contained.

Used for:
- writing AI interaction audit logs (keeps AI-call latency off the
  logging path)
- recomputing low-stock alerts after a consumption log or stock update
- writing anonymized eligibility-check outcomes
"""

from typing import Any, Dict, Optional

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.models.alert import Alert, AlertSeverity, AlertType
from app.repositories.ai_log_repository import AIInteractionLogRepository, EligibilityCheckLogRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.inventory_repository import MedicineStockRepository
from app.models.ai_log import AIInteractionLog, EligibilityCheckLog

logger = get_logger(__name__)


def log_ai_interaction(
    *,
    module: str,
    provider_used: str,
    prompt_template_version: str,
    input_hash: str,
    output_summary: str,
    guardrail_flags: Dict[str, Any],
    succeeded: bool,
) -> None:
    db = SessionLocal()
    try:
        repo = AIInteractionLogRepository(db)
        repo.add(
            AIInteractionLog(
                module=module,
                provider_used=provider_used,
                prompt_template_version=prompt_template_version,
                input_hash=input_hash,
                output_summary=output_summary[:2000],
                guardrail_flags=guardrail_flags,
                succeeded=succeeded,
            )
        )
        db.commit()
    except Exception:  # noqa: BLE001 — logging must never raise into the caller
        db.rollback()
        logger.error("failed_to_write_ai_interaction_log", exc_info=True)
    finally:
        db.close()


def log_eligibility_check(*, phc_id: Optional[int], scheme_id: int, is_eligible: bool, checked_by_role: str) -> None:
    db = SessionLocal()
    try:
        repo = EligibilityCheckLogRepository(db)
        repo.add(
            EligibilityCheckLog(
                phc_id=phc_id, scheme_id=scheme_id, is_eligible=is_eligible, checked_by_role=checked_by_role
            )
        )
        db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()
        logger.error("failed_to_write_eligibility_check_log", exc_info=True)
    finally:
        db.close()


def refresh_low_stock_alerts(phc_id: int) -> None:
    """Re-evaluates every medicine's stock for a PHC against its reorder
    threshold and opens a new LOW_STOCK alert for any medicine that has
    crossed the threshold and doesn't already have an open alert. Triggered
    after any stock quantity or consumption change."""
    db = SessionLocal()
    try:
        stock_repo = MedicineStockRepository(db)
        alert_repo = AlertRepository(db)

        stocks = stock_repo.list_for_phc(phc_id)
        for stock in stocks:
            medicine = stock.medicine
            if stock.quantity <= medicine.reorder_threshold:
                message = f"{medicine.name} stock ({stock.quantity} {medicine.unit}) is at or below reorder threshold ({medicine.reorder_threshold})."
                if not alert_repo.exists_open_alert(phc_id, AlertType.LOW_STOCK, message):
                    severity = AlertSeverity.CRITICAL if stock.quantity == 0 else AlertSeverity.HIGH
                    alert_repo.add(
                        Alert(phc_id=phc_id, type=AlertType.LOW_STOCK, severity=severity, message=message)
                    )
        db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()
        logger.error("failed_to_refresh_low_stock_alerts", phc_id=phc_id, exc_info=True)
    finally:
        db.close()
