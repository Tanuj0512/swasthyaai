from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import AIExplanation


class DistrictOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    state: str


class PHCStatusSummary(BaseModel):
    phc_id: int
    phc_name: str
    low_stock_medicine_count: int
    doctor_absence_rate: float
    bed_occupancy_rate: float
    footfall_7day_total: int
    open_alert_count: int
    attention_score: float  # higher = needs more attention


class DistrictSummaryResponse(BaseModel):
    district_id: int
    district_name: str
    phc_statuses: List[PHCStatusSummary]


class CopilotQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)


class CopilotQueryResponse(BaseModel):
    summary: DistrictSummaryResponse
    explanation: AIExplanation
