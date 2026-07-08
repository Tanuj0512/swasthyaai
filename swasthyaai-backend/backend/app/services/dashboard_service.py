from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories.alert_repository import AlertRepository
from app.repositories.district_repository import PHCRepository
from app.repositories.inventory_repository import MedicineStockRepository
from app.repositories.operations_repository import (
    BedRepository,
    DoctorAttendanceRepository,
    DoctorRepository,
    PatientFootfallRepository,
)
from app.schemas.dashboard import (
    AlertOut,
    BedSummary,
    DashboardSnapshot,
    DoctorAttendanceSummary,
    FootfallSummary,
    PHCOut,
    StockSummary,
)


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.phc_repo = PHCRepository(db)
        self.stock_repo = MedicineStockRepository(db)
        self.bed_repo = BedRepository(db)
        self.doctor_repo = DoctorRepository(db)
        self.attendance_repo = DoctorAttendanceRepository(db)
        self.footfall_repo = PatientFootfallRepository(db)
        self.alert_repo = AlertRepository(db)

    def list_phcs(self) -> list[PHCOut]:
        phcs = self.phc_repo.list_all()
        return [PHCOut.model_validate(p) for p in phcs]

    def get_dashboard(self, phc_id: int) -> DashboardSnapshot:
        phc = self.phc_repo.get(phc_id)
        if phc is None:
            raise NotFoundError(f"PHC {phc_id} was not found.")

        stocks = self.stock_repo.list_for_phc(phc_id)
        stock_summaries = [
            StockSummary(
                medicine_id=s.medicine_id,
                medicine_name=s.medicine.name,
                quantity=s.quantity,
                reorder_threshold=s.medicine.reorder_threshold,
                unit=s.medicine.unit,
                is_low=s.quantity <= s.medicine.reorder_threshold,
            )
            for s in stocks
        ]

        beds = self.bed_repo.list_for_phc(phc_id)
        bed_summaries = [
            BedSummary(
                ward_type=b.ward_type,
                total_beds=b.total_beds,
                occupied_beds=b.occupied_beds,
                occupancy_rate=round(b.occupied_beds / b.total_beds, 2) if b.total_beds else 0.0,
            )
            for b in beds
        ]

        doctors = self.doctor_repo.list_for_phc(phc_id)
        today = date.today()
        attendance_today = self.attendance_repo.list_for_date([d.id for d in doctors], today)
        attendance_by_doctor = {a.doctor_id: a for a in attendance_today}
        attendance_summaries = [
            DoctorAttendanceSummary(
                doctor_id=d.id,
                doctor_name=d.name,
                specialization=d.specialization,
                status=attendance_by_doctor[d.id].status.value if d.id in attendance_by_doctor else "not_marked",
            )
            for d in doctors
        ]

        week_ago = today - timedelta(days=7)
        footfall = self.footfall_repo.list_for_phc_range(phc_id, week_ago, today)
        footfall_summaries = [
            FootfallSummary(date=f.date, department=f.department, count=f.count) for f in footfall
        ]

        alerts = self.alert_repo.list_for_phc(phc_id, unresolved_only=True, limit=10)
        alert_outs = [AlertOut.model_validate(a) for a in alerts]

        return DashboardSnapshot(
            phc=PHCOut.model_validate(phc),
            medicine_inventory=stock_summaries,
            beds=bed_summaries,
            doctor_attendance_today=attendance_summaries,
            footfall_last_7_days=footfall_summaries,
            recent_alerts=alert_outs,
        )
