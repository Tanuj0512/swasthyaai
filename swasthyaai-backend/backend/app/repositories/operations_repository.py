from datetime import date
from typing import List

from sqlalchemy import select

from app.models.operations import Bed, Doctor, DoctorAttendance, PatientFootfall
from app.repositories.base import BaseRepository


class BedRepository(BaseRepository[Bed]):
    model = Bed

    def list_for_phc(self, phc_id: int) -> List[Bed]:
        return list(self.db.execute(select(Bed).where(Bed.phc_id == phc_id)).scalars().all())


class DoctorRepository(BaseRepository[Doctor]):
    model = Doctor

    def list_for_phc(self, phc_id: int) -> List[Doctor]:
        return list(self.db.execute(select(Doctor).where(Doctor.phc_id == phc_id)).scalars().all())


class DoctorAttendanceRepository(BaseRepository[DoctorAttendance]):
    model = DoctorAttendance

    def list_for_date(self, doctor_ids: List[int], on_date: date) -> List[DoctorAttendance]:
        stmt = select(DoctorAttendance).where(
            DoctorAttendance.doctor_id.in_(doctor_ids), DoctorAttendance.date == on_date
        )
        return list(self.db.execute(stmt).scalars().all())


class PatientFootfallRepository(BaseRepository[PatientFootfall]):
    model = PatientFootfall

    def list_for_phc_range(self, phc_id: int, start: date, end: date) -> List[PatientFootfall]:
        stmt = select(PatientFootfall).where(
            PatientFootfall.phc_id == phc_id,
            PatientFootfall.date >= start,
            PatientFootfall.date <= end,
        )
        return list(self.db.execute(stmt).scalars().all())
