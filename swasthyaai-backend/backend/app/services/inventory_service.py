import hashlib
from typing import List, Optional

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.ai.orchestrator import AIOrchestrator
from app.ai.prompts.inventory_prompts import (
    INVENTORY_EXPLANATION_SYSTEM_INSTRUCTION,
    PROMPT_VERSION,
    build_inventory_explanation_prompt,
)
from app.background.tasks import log_ai_interaction, refresh_low_stock_alerts
from app.core.cache import cache_response, clear_cache
from app.core.exceptions import NotFoundError
from app.domain.inventory_engine import (
    ForecastInput,
    PHCStockSnapshot,
    compute_forecast,
    compute_redistribution_suggestions,
)
from app.models.inventory import MedicineConsumptionLog
from app.repositories.district_repository import PHCRepository
from app.repositories.inventory_repository import (
    MedicineConsumptionRepository,
    MedicineStockRepository,
)
from app.schemas.common import AIExplanation
from app.schemas.inventory import (
    InventoryForecastResponse,
    InventoryRecommendationResponse,
    MedicineForecast,
    RedistributionSuggestion,
)

FORECAST_WINDOW_DAYS = 14


class InventoryService:
    def __init__(self, db: Session, orchestrator: Optional[AIOrchestrator] = None):
        self.db = db
        self.phc_repo = PHCRepository(db)
        self.stock_repo = MedicineStockRepository(db)
        self.consumption_repo = MedicineConsumptionRepository(db)
        self.orchestrator = orchestrator or AIOrchestrator()

    def _build_forecast(self, phc_id: int) -> List[MedicineForecast]:
        stocks = self.stock_repo.list_for_phc(phc_id)
        forecasts: List[MedicineForecast] = []
        for stock in stocks:
            logs = self.consumption_repo.list_recent(phc_id, stock.medicine_id, FORECAST_WINDOW_DAYS)
            forecast_input = ForecastInput(
                medicine_id=stock.medicine_id,
                medicine_name=stock.medicine.name,
                current_quantity=stock.quantity,
                reorder_threshold=stock.medicine.reorder_threshold,
                consumption_last_n_days=[log.quantity_used for log in logs],
                window_days=FORECAST_WINDOW_DAYS,
            )
            result = compute_forecast(forecast_input)
            forecasts.append(
                MedicineForecast(
                    medicine_id=result.medicine_id,
                    medicine_name=result.medicine_name,
                    current_quantity=result.current_quantity,
                    reorder_threshold=result.reorder_threshold,
                    avg_daily_consumption=result.avg_daily_consumption,
                    predicted_days_until_stockout=result.predicted_days_until_stockout,
                    is_low_stock=result.is_low_stock,
                )
            )
        return forecasts

    @cache_response()
    def get_forecast(self, phc_id: int) -> InventoryForecastResponse:
        phc = self.phc_repo.get(phc_id)
        if phc is None:
            raise NotFoundError(f"PHC {phc_id} was not found.")
        return InventoryForecastResponse(phc_id=phc_id, forecasts=self._build_forecast(phc_id))

    def log_consumption(self, phc_id: int, medicine_id: int, quantity_used: int, background_tasks: BackgroundTasks) -> None:
        phc = self.phc_repo.get(phc_id)
        if phc is None:
            raise NotFoundError(f"PHC {phc_id} was not found.")

        stock = self.stock_repo.get_for_phc_and_medicine(phc_id, medicine_id)
        if stock is None:
            raise NotFoundError(f"No stock record for medicine {medicine_id} at PHC {phc_id}.")

        self.consumption_repo.add(
            MedicineConsumptionLog(phc_id=phc_id, medicine_id=medicine_id, quantity_used=quantity_used)
        )
        stock.quantity = max(stock.quantity - quantity_used, 0)
        self.consumption_repo.commit()
        clear_cache()
        background_tasks.add_task(refresh_low_stock_alerts, phc_id)

    def get_recommendations(
        self, phc_id: int, background_tasks: Optional[BackgroundTasks] = None
    ) -> InventoryRecommendationResponse:
        phc = self.phc_repo.get(phc_id)
        if phc is None:
            raise NotFoundError(f"PHC {phc_id} was not found.")

        forecasts = self._build_forecast(phc_id)
        low_stock = [f for f in forecasts if f.is_low_stock]

        redistribution_suggestions: List[RedistributionSuggestion] = []
        for low in low_stock:
            stocks_for_medicine = self.stock_repo.list_for_medicine_across_phcs(low.medicine_id)
            snapshots = []
            for s in stocks_for_medicine:
                phc_for_stock = self.phc_repo.get(s.phc_id)
                if phc_for_stock is None:
                    continue
                snapshots.append(
                    PHCStockSnapshot(
                        phc_id=s.phc_id,
                        phc_name=phc_for_stock.name,
                        quantity=s.quantity,
                        reorder_threshold=s.medicine.reorder_threshold,
                    )
                )
            suggestions = compute_redistribution_suggestions(low.medicine_id, low.medicine_name, snapshots)
            for sug in suggestions:
                if sug.to_phc_id == phc_id:
                    redistribution_suggestions.append(
                        RedistributionSuggestion(
                            medicine_id=low.medicine_id,
                            medicine_name=low.medicine_name,
                            from_phc_id=sug.from_phc_id,
                            from_phc_name=sug.from_phc_name,
                            to_phc_id=sug.to_phc_id,
                            to_phc_name=sug.to_phc_name,
                            suggested_quantity=sug.suggested_quantity,
                        )
                    )

        forecast_blocks = "\n".join(
            f"- {f.medicine_name}: {f.current_quantity} units in stock, reorder threshold {f.reorder_threshold}, "
            f"average daily consumption {f.avg_daily_consumption}, "
            f"{'predicted stockout in ' + str(f.predicted_days_until_stockout) + ' days' if f.predicted_days_until_stockout is not None else 'no recent consumption data'}"
            for f in low_stock
        ) or "No medicines are currently below their reorder threshold."

        redistribution_blocks = "\n".join(
            f"- Move {s.suggested_quantity} units of {s.medicine_name} from {s.from_phc_name} to {s.to_phc_name}"
            for s in redistribution_suggestions
        )

        fallback_text = self._build_fallback_explanation(phc.name, low_stock, redistribution_suggestions)

        grounding_terms = [phc.name] + [f.medicine_name for f in low_stock] + [
            s.from_phc_name for s in redistribution_suggestions
        ] + [s.to_phc_name for s in redistribution_suggestions]

        result = self.orchestrator.generate_grounded_explanation(
            system_instruction_base=INVENTORY_EXPLANATION_SYSTEM_INSTRUCTION,
            user_prompt=build_inventory_explanation_prompt(phc.name, forecast_blocks, redistribution_blocks),
            grounding_terms=grounding_terms,
            fallback_text=fallback_text,
        )

        input_hash = hashlib.sha256(f"{phc_id}:{forecast_blocks}".encode()).hexdigest()
        if background_tasks is not None:
            background_tasks.add_task(
                log_ai_interaction,
                module="inventory",
                provider_used=result.provider,
                prompt_template_version=PROMPT_VERSION,
                input_hash=input_hash,
                output_summary=result.text,
                guardrail_flags=result.guardrail_flags,
                succeeded=result.succeeded,
            )

        return InventoryRecommendationResponse(
            phc_id=phc_id,
            low_stock_forecasts=low_stock,
            redistribution_suggestions=redistribution_suggestions,
            explanation=AIExplanation(text=result.text, provider=result.provider, grounded=result.grounded),
        )

    @staticmethod
    def _build_fallback_explanation(phc_name: str, low_stock, suggestions) -> str:
        if not low_stock:
            return f"All medicines at {phc_name} are currently above their reorder threshold."
        lines = [f"At {phc_name}, the following medicines need attention:"]
        for f in low_stock:
            if f.predicted_days_until_stockout is not None:
                lines.append(
                    f"- {f.medicine_name}: {f.current_quantity} units left, "
                    f"expected to run out in about {f.predicted_days_until_stockout} days at current usage."
                )
            else:
                lines.append(
                    f"- {f.medicine_name}: {f.current_quantity} units left, at or below the reorder threshold."
                )
        if suggestions:
            lines.append("Suggested redistribution:")
            for s in suggestions:
                lines.append(f"- Move {s.suggested_quantity} units of {s.medicine_name} from {s.from_phc_name}.")
        return "\n".join(lines)
