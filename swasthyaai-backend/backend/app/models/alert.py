import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntPKMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.district import PHC


class AlertType(str, enum.Enum):
    LOW_STOCK = "low_stock"
    BED_FULL = "bed_full"
    DOCTOR_ABSENT = "doctor_absent"


class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Alert(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "alerts"

    phc_id: Mapped[int] = mapped_column(ForeignKey("phcs.id"), nullable=False)
    type: Mapped[AlertType] = mapped_column(Enum(AlertType, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    phc: Mapped["PHC"] = relationship()
