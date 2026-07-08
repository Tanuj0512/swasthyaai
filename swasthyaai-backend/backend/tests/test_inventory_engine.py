from app.domain.inventory_engine import (
    ForecastInput,
    PHCStockSnapshot,
    compute_forecast,
    compute_redistribution_suggestions,
)


class TestComputeForecast:
    def test_low_stock_flagged_when_below_threshold(self):
        data = ForecastInput(
            medicine_id=1, medicine_name="Test Med", current_quantity=5, reorder_threshold=20,
            consumption_last_n_days=[2, 2, 2], window_days=14,
        )
        result = compute_forecast(data)
        assert result.is_low_stock is True

    def test_not_low_stock_when_well_above_threshold_and_slow_consumption(self):
        data = ForecastInput(
            medicine_id=1, medicine_name="Test Med", current_quantity=500, reorder_threshold=20,
            consumption_last_n_days=[1], window_days=14,
        )
        result = compute_forecast(data)
        assert result.is_low_stock is False

    def test_no_consumption_yields_no_stockout_prediction(self):
        data = ForecastInput(
            medicine_id=1, medicine_name="Test Med", current_quantity=100, reorder_threshold=20,
            consumption_last_n_days=[], window_days=14,
        )
        result = compute_forecast(data)
        assert result.predicted_days_until_stockout is None

    def test_stockout_prediction_flags_low_stock_even_above_threshold(self):
        # 200 units, threshold 20 (well above), but burning 50/day -> stockout in 4 days
        data = ForecastInput(
            medicine_id=1, medicine_name="Test Med", current_quantity=200, reorder_threshold=20,
            consumption_last_n_days=[50] * 14, window_days=14,
        )
        result = compute_forecast(data)
        assert result.predicted_days_until_stockout == 4.0
        assert result.is_low_stock is True


class TestRedistributionSuggestions:
    def test_suggests_transfer_from_surplus_to_deficit(self):
        snapshots = [
            PHCStockSnapshot(phc_id=1, phc_name="PHC A (deficit)", quantity=5, reorder_threshold=20),
            PHCStockSnapshot(phc_id=2, phc_name="PHC B (surplus)", quantity=200, reorder_threshold=20),
        ]
        suggestions = compute_redistribution_suggestions(1, "Test Med", snapshots)
        assert len(suggestions) == 1
        assert suggestions[0].from_phc_id == 2
        assert suggestions[0].to_phc_id == 1
        assert suggestions[0].suggested_quantity > 0

    def test_no_suggestion_when_no_surplus_available(self):
        snapshots = [
            PHCStockSnapshot(phc_id=1, phc_name="PHC A (deficit)", quantity=5, reorder_threshold=20),
            PHCStockSnapshot(phc_id=2, phc_name="PHC B (also low)", quantity=10, reorder_threshold=20),
        ]
        suggestions = compute_redistribution_suggestions(1, "Test Med", snapshots)
        assert suggestions == []

    def test_transfer_never_exceeds_half_of_surplus(self):
        snapshots = [
            PHCStockSnapshot(phc_id=1, phc_name="PHC A (deficit)", quantity=0, reorder_threshold=20),
            PHCStockSnapshot(phc_id=2, phc_name="PHC B (surplus)", quantity=100, reorder_threshold=20),
        ]
        suggestions = compute_redistribution_suggestions(1, "Test Med", snapshots)
        surplus_above_threshold = 100 - 20
        assert suggestions[0].suggested_quantity <= surplus_above_threshold / 2 + 1
