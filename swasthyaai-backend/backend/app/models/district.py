from typing import List, Optional

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntPKMixin, TimestampMixin


class District(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "districts"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    state: Mapped[str] = mapped_column(String(120), nullable=False)

    phcs: Mapped[List["PHC"]] = relationship(back_populates="district")


class PHC(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "phcs"

    district_id: Mapped[int] = mapped_column(ForeignKey("districts.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    district: Mapped["District"] = relationship(back_populates="phcs")
