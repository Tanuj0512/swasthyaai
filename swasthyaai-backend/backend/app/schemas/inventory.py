from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import AIExplanation


class ConsumptionLogRequest(BaseModel):
    medicine_id: int
    quantity_used: int = Field(..., gt=0)


class MedicineForecast(BaseModel):
    medicine_id: int
    medicine_name: str
    current_quantity: int
    reorder_threshold: int
    avg_daily_consumption: float
    predicted_days_until_stockout: Optional[float]
    is_low_stock: bool


class RedistributionSuggestion(BaseModel):
    medicine_id: int
    medicine_name: str
    from_phc_id: int
    from_phc_name: str
    to_phc_id: int
    to_phc_name: str
    suggested_quantity: int


class InventoryForecastResponse(BaseModel):
    phc_id: int
    forecasts: List[MedicineForecast]


class InventoryRecommendationResponse(BaseModel):
    phc_id: int
    low_stock_forecasts: List[MedicineForecast]
    redistribution_suggestions: List[RedistributionSuggestion]
    explanation: AIExplanation
