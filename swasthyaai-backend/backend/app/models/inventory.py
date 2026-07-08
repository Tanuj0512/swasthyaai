from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntPKMixin, TimestampMixin, utcnow

if TYPE_CHECKING:
    from app.models.district import PHC


class Medicine(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "medicines"

    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)  # e.g. "strip", "bottle", "vial"
    reorder_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=20)


class MedicineStock(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "medicine_stock"
    __table_args__ = (UniqueConstraint("phc_id", "medicine_id", name="uq_stock_phc_medicine"),)

    phc_id: Mapped[int] = mapped_column(ForeignKey("phcs.id"), nullable=False)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    medicine: Mapped["Medicine"] = relationship()
    phc: Mapped["PHC"] = relationship()


class MedicineConsumptionLog(Base, IntPKMixin):
    __tablename__ = "medicine_consumption_log"

    phc_id: Mapped[int] = mapped_column(ForeignKey("phcs.id"), nullable=False)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id"), nullable=False)
    quantity_used: Mapped[int] = mapped_column(Integer, nullable=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    medicine: Mapped["Medicine"] = relationship()
    phc: Mapped["PHC"] = relationship()
