import enum
from datetime import date as date_type
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntPKMixin, TimestampMixin, utcnow

if TYPE_CHECKING:
    from app.models.district import PHC


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    ON_LEAVE = "leave"


class Bed(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "beds"

    phc_id: Mapped[int] = mapped_column(ForeignKey("phcs.id"), nullable=False)
    ward_type: Mapped[str] = mapped_column(String(80), nullable=False)  # general, maternity, ICU...
    total_beds: Mapped[int] = mapped_column(Integer, nullable=False)
    occupied_beds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    phc: Mapped["PHC"] = relationship()


class Doctor(Base, IntPKMixin, TimestampMixin):
    __tablename__ = "doctors"

    phc_id: Mapped[int] = mapped_column(ForeignKey("phcs.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    specialization: Mapped[str] = mapped_column(String(100), nullable=False)

    attendance_records: Mapped[list["DoctorAttendance"]] = relationship(back_populates="doctor")
    phc: Mapped["PHC"] = relationship()


class DoctorAttendance(Base, IntPKMixin):
    __tablename__ = "doctor_attendance"

    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    status: Mapped[AttendanceStatus] = mapped_column(Enum(AttendanceStatus, values_callable=lambda obj: [e.value for e in obj]), nullable=False)
    marked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    doctor: Mapped["Doctor"] = relationship(back_populates="attendance_records")


class PatientFootfall(Base, IntPKMixin):
    __tablename__ = "patient_footfall"

    phc_id: Mapped[int] = mapped_column(ForeignKey("phcs.id"), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    phc: Mapped["PHC"] = relationship()
