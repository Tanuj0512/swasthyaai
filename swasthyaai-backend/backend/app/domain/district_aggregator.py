"""
Computes a per-PHC 'attention score' from raw operational counts. Purely
arithmetic — the AI layer only summarizes the ranked output of this module,
it never recomputes or second-guesses these numbers.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class PHCRawStatus:
    phc_id: int
    phc_name: str
    low_stock_medicine_count: int
    doctors_total: int
    doctors_absent_today: int
    total_beds: int
    occupied_beds: int
    footfall_7day_total: int
    open_alert_count: int


@dataclass
class PHCScoredStatus:
    phc_id: int
    phc_name: str
    low_stock_medicine_count: int
    doctor_absence_rate: float
    bed_occupancy_rate: float
    footfall_7day_total: int
    open_alert_count: int
    attention_score: float


# Weights are intentionally simple and documented — a health officer should
# be able to sanity-check this score by hand, not treat it as a black box.
_WEIGHT_LOW_STOCK = 2.0
_WEIGHT_DOCTOR_ABSENCE = 3.0
_WEIGHT_BED_OCCUPANCY = 2.0
_WEIGHT_OPEN_ALERTS = 1.5


def score_phc(status: PHCRawStatus) -> PHCScoredStatus:
    doctor_absence_rate = (
        status.doctors_absent_today / status.doctors_total if status.doctors_total > 0 else 0.0
    )
    bed_occupancy_rate = (
        status.occupied_beds / status.total_beds if status.total_beds > 0 else 0.0
    )

    attention_score = (
        status.low_stock_medicine_count * _WEIGHT_LOW_STOCK
        + doctor_absence_rate * _WEIGHT_DOCTOR_ABSENCE
        + max(bed_occupancy_rate - 0.85, 0) * 10 * _WEIGHT_BED_OCCUPANCY  # penalize only when near-full
        + status.open_alert_count * _WEIGHT_OPEN_ALERTS
    )

    return PHCScoredStatus(
        phc_id=status.phc_id,
        phc_name=status.phc_name,
        low_stock_medicine_count=status.low_stock_medicine_count,
        doctor_absence_rate=round(doctor_absence_rate, 2),
        bed_occupancy_rate=round(bed_occupancy_rate, 2),
        footfall_7day_total=status.footfall_7day_total,
        open_alert_count=status.open_alert_count,
        attention_score=round(attention_score, 2),
    )


def rank_phcs(statuses: List[PHCRawStatus]) -> List[PHCScoredStatus]:
    scored = [score_phc(s) for s in statuses]
    return sorted(scored, key=lambda s: s.attention_score, reverse=True)
