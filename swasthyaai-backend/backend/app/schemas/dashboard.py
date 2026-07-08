from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class PHCOut(BaseModel):
    id: int
    name: str
    district_id: int
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    contact_phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StockSummary(BaseModel):
    medicine_id: int
    medicine_name: str
    quantity: int
    reorder_threshold: int
    unit: str
    is_low: bool


class BedSummary(BaseModel):
    ward_type: str
    total_beds: int
    occupied_beds: int
    occupancy_rate: float


class DoctorAttendanceSummary(BaseModel):
    doctor_id: int
    doctor_name: str
    specialization: str
    status: str


class FootfallSummary(BaseModel):
    date: date
    department: str
    count: int


class AlertOut(BaseModel):
    id: int
    type: str
    severity: str
    message: str
    resolved: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardSnapshot(BaseModel):
    phc: PHCOut
    medicine_inventory: List[StockSummary]
    beds: List[BedSummary]
    doctor_attendance_today: List[DoctorAttendanceSummary]
    footfall_last_7_days: List[FootfallSummary]
    recent_alerts: List[AlertOut]
