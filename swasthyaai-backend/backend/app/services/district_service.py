import hashlib
from datetime import date, timedelta
from typing import List, Optional

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.ai.orchestrator import AIOrchestrator
from app.ai.prompts.district_prompts import (
    DISTRICT_SUMMARY_SYSTEM_INSTRUCTION,
    PROMPT_VERSION,
    build_district_summary_prompt,
)
from app.background.tasks import log_ai_interaction
from app.core.cache import cache_response
from app.core.exceptions import NotFoundError
from app.domain.district_aggregator import PHCRawStatus, rank_phcs
from app.repositories.alert_repository import AlertRepository
from app.repositories.district_repository import DistrictRepository, PHCRepository
from app.repositories.inventory_repository import MedicineStockRepository
from app.repositories.operations_repository import (
    BedRepository,
    DoctorAttendanceRepository,
    DoctorRepository,
    PatientFootfallRepository,
)
from app.schemas.common import AIExplanation
from app.schemas.district import CopilotQueryResponse, DistrictOut, DistrictSummaryResponse, PHCStatusSummary


class DistrictService:
    def __init__(self, db: Session, orchestrator: Optional[AIOrchestrator] = None):
        self.db = db
        self.district_repo = DistrictRepository(db)
        self.phc_repo = PHCRepository(db)
        self.stock_repo = MedicineStockRepository(db)
        self.bed_repo = BedRepository(db)
        self.doctor_repo = DoctorRepository(db)
        self.attendance_repo = DoctorAttendanceRepository(db)
        self.footfall_repo = PatientFootfallRepository(db)
        self.alert_repo = AlertRepository(db)
        self.orchestrator = orchestrator or AIOrchestrator()

    def list_districts(self) -> List[DistrictOut]:
        return [DistrictOut.model_validate(d) for d in self.district_repo.list()]

    @cache_response()
    def get_district_summary(self, district_id: int) -> DistrictSummaryResponse:
        district = self.district_repo.get(district_id)
        if district is None:
            raise NotFoundError(f"District {district_id} was not found.")

        phcs = self.phc_repo.list_by_district(district_id)
        today = date.today()
        week_ago = today - timedelta(days=7)

        raw_statuses: List[PHCRawStatus] = []
        for phc in phcs:
            stocks = self.stock_repo.list_for_phc(phc.id)
            low_stock_count = sum(1 for s in stocks if s.quantity <= s.medicine.reorder_threshold)

            doctors = self.doctor_repo.list_for_phc(phc.id)
            attendance_today = self.attendance_repo.list_for_date([d.id for d in doctors], today)
            absent_today = sum(1 for a in attendance_today if a.status.value == "absent")

            beds = self.bed_repo.list_for_phc(phc.id)
            total_beds = sum(b.total_beds for b in beds)
            occupied_beds = sum(b.occupied_beds for b in beds)

            footfall = self.footfall_repo.list_for_phc_range(phc.id, week_ago, today)
            footfall_total = sum(f.count for f in footfall)

            open_alerts = self.alert_repo.list_for_phc(phc.id, unresolved_only=True, limit=1000)

            raw_statuses.append(
                PHCRawStatus(
                    phc_id=phc.id,
                    phc_name=phc.name,
                    low_stock_medicine_count=low_stock_count,
                    doctors_total=len(doctors),
                    doctors_absent_today=absent_today,
                    total_beds=total_beds,
                    occupied_beds=occupied_beds,
                    footfall_7day_total=footfall_total,
                    open_alert_count=len(open_alerts),
                )
            )

        ranked = rank_phcs(raw_statuses)
        phc_statuses = [
            PHCStatusSummary(
                phc_id=r.phc_id,
                phc_name=r.phc_name,
                low_stock_medicine_count=r.low_stock_medicine_count,
                doctor_absence_rate=r.doctor_absence_rate,
                bed_occupancy_rate=r.bed_occupancy_rate,
                footfall_7day_total=r.footfall_7day_total,
                open_alert_count=r.open_alert_count,
                attention_score=r.attention_score,
            )
            for r in ranked
        ]

        return DistrictSummaryResponse(district_id=district_id, district_name=district.name, phc_statuses=phc_statuses)

    def answer_copilot_query(
        self, district_id: int, question: str, background_tasks: Optional[BackgroundTasks] = None
    ) -> CopilotQueryResponse:
        summary = self.get_district_summary(district_id)

        top_phcs = summary.phc_statuses[:5]
        status_blocks = "\n".join(
            f"- {p.phc_name}: attention score {p.attention_score}, {p.low_stock_medicine_count} medicines low on stock, "
            f"{int(p.doctor_absence_rate * 100)}% doctor absence today, {int(p.bed_occupancy_rate * 100)}% bed occupancy, "
            f"{p.footfall_7day_total} patients in last 7 days, {p.open_alert_count} open alerts"
            for p in top_phcs
        ) or "No PHC data available for this district."

        fallback_text = "PHCs needing the most attention today:\n" + "\n".join(
            f"- {p.phc_name} (score {p.attention_score})" for p in top_phcs
        )

        result = self.orchestrator.generate_grounded_explanation(
            system_instruction_base=DISTRICT_SUMMARY_SYSTEM_INSTRUCTION,
            user_prompt=build_district_summary_prompt(question, summary.district_name, status_blocks),
            grounding_terms=[p.phc_name for p in top_phcs] + [summary.district_name],
            fallback_text=fallback_text,
        )

        input_hash = hashlib.sha256(status_blocks.encode()).hexdigest()
        if background_tasks is not None:
            background_tasks.add_task(
                log_ai_interaction,
                module="district_copilot",
                provider_used=result.provider,
                prompt_template_version=PROMPT_VERSION,
                input_hash=input_hash,
                output_summary=result.text,
                guardrail_flags=result.guardrail_flags,
                succeeded=result.succeeded,
            )

        return CopilotQueryResponse(
            summary=summary,
            explanation=AIExplanation(text=result.text, provider=result.provider, grounded=result.grounded),
        )
