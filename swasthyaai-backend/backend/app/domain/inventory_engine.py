"""
All arithmetic for Module 2. The AI layer only ever explains numbers this
module already computed — it never invents a forecast or a redistribution
quantity itself, per the "backend performs calculations, AI explains"
requirement.
"""

from dataclasses import dataclass
from typing import List, Optional

DEFAULT_STOCKOUT_ALERT_DAYS = 7


@dataclass
class ForecastInput:
    medicine_id: int
    medicine_name: str
    current_quantity: int
    reorder_threshold: int
    consumption_last_n_days: List[int]  # one entry per logged consumption event
    window_days: int


@dataclass
class ForecastOutput:
    medicine_id: int
    medicine_name: str
    current_quantity: int
    reorder_threshold: int
    avg_daily_consumption: float
    predicted_days_until_stockout: Optional[float]
    is_low_stock: bool


def compute_forecast(data: ForecastInput) -> ForecastOutput:
    total_consumed = sum(data.consumption_last_n_days)
    avg_daily = total_consumed / data.window_days if data.window_days > 0 else 0.0

    predicted_days: Optional[float]
    if avg_daily > 0:
        predicted_days = round(data.current_quantity / avg_daily, 1)
    else:
        predicted_days = None  # no recent consumption — cannot estimate a stockout date

    is_low_stock = data.current_quantity <= data.reorder_threshold or (
        predicted_days is not None and predicted_days <= DEFAULT_STOCKOUT_ALERT_DAYS
    )

    return ForecastOutput(
        medicine_id=data.medicine_id,
        medicine_name=data.medicine_name,
        current_quantity=data.current_quantity,
        reorder_threshold=data.reorder_threshold,
        avg_daily_consumption=round(avg_daily, 2),
        predicted_days_until_stockout=predicted_days,
        is_low_stock=is_low_stock,
    )


@dataclass
class PHCStockSnapshot:
    phc_id: int
    phc_name: str
    quantity: int
    reorder_threshold: int


@dataclass
class RedistributionSuggestionOutput:
    from_phc_id: int
    from_phc_name: str
    to_phc_id: int
    to_phc_name: str
    suggested_quantity: int


def compute_redistribution_suggestions(
    medicine_id: int,
    medicine_name: str,
    snapshots: List[PHCStockSnapshot],
    surplus_multiplier: float = 2.0,
) -> List[RedistributionSuggestionOutput]:
    """
    Simple, explainable heuristic (deliberately not a solver): a PHC counts
    as a surplus source if its stock is at least `surplus_multiplier` times
    its own reorder threshold; a PHC counts as in deficit if it's at or
    below threshold. Transfer amount is capped at half the source's surplus
    so no single transfer empties out a well-stocked PHC. This is easy to
    explain to a health officer and easy to override manually — a fully
    optimal transportation-problem solver would be harder to justify for an
    MVP and harder for a human to sanity-check.
    """
    deficits = [s for s in snapshots if s.quantity <= s.reorder_threshold]
    surpluses = [s for s in snapshots if s.quantity >= s.reorder_threshold * surplus_multiplier]

    suggestions: List[RedistributionSuggestionOutput] = []
    surplus_pool = {s.phc_id: s.quantity - s.reorder_threshold for s in surpluses}

    for deficit in deficits:
        needed = deficit.reorder_threshold - deficit.quantity
        if needed <= 0:
            continue
        for surplus in surpluses:
            available = surplus_pool.get(surplus.phc_id, 0) // 2
            if available <= 0 or surplus.phc_id == deficit.phc_id:
                continue
            transfer = min(available, needed)
            if transfer <= 0:
                continue
            suggestions.append(
                RedistributionSuggestionOutput(
                    from_phc_id=surplus.phc_id,
                    from_phc_name=surplus.phc_name,
                    to_phc_id=deficit.phc_id,
                    to_phc_name=deficit.phc_name,
                    suggested_quantity=transfer,
                )
            )
            surplus_pool[surplus.phc_id] -= transfer
            needed -= transfer
            if needed <= 0:
                break

    return suggestions
