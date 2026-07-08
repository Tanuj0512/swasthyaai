from app.domain.district_aggregator import PHCRawStatus, rank_phcs, score_phc


def make_status(**overrides) -> PHCRawStatus:
    defaults = dict(
        phc_id=1, phc_name="Test PHC", low_stock_medicine_count=0, doctors_total=5,
        doctors_absent_today=0, total_beds=20, occupied_beds=5, footfall_7day_total=100,
        open_alert_count=0,
    )
    defaults.update(overrides)
    return PHCRawStatus(**defaults)


class TestScorePHC:
    def test_healthy_phc_scores_lower_than_troubled_phc(self):
        healthy = score_phc(make_status())
        troubled = score_phc(
            make_status(low_stock_medicine_count=10, doctors_absent_today=4, occupied_beds=19, open_alert_count=5)
        )
        assert troubled.attention_score > healthy.attention_score

    def test_zero_doctors_does_not_divide_by_zero(self):
        result = score_phc(make_status(doctors_total=0, doctors_absent_today=0))
        assert result.doctor_absence_rate == 0.0

    def test_zero_beds_does_not_divide_by_zero(self):
        result = score_phc(make_status(total_beds=0, occupied_beds=0))
        assert result.bed_occupancy_rate == 0.0

    def test_near_full_occupancy_penalized_more_than_moderate_occupancy(self):
        moderate = score_phc(make_status(total_beds=20, occupied_beds=10))  # 50%
        near_full = score_phc(make_status(total_beds=20, occupied_beds=19))  # 95%
        assert near_full.attention_score > moderate.attention_score


class TestRankPHCs:
    def test_ranked_descending_by_attention_score(self):
        statuses = [
            make_status(phc_id=1, phc_name="Low concern"),
            make_status(phc_id=2, phc_name="High concern", low_stock_medicine_count=15, open_alert_count=8),
            make_status(phc_id=3, phc_name="Medium concern", low_stock_medicine_count=3),
        ]
        ranked = rank_phcs(statuses)
        assert ranked[0].phc_name == "High concern"
        assert ranked[-1].phc_name == "Low concern"
