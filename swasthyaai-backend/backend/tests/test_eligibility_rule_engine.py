import pytest

from app.core.exceptions import RuleEngineError
from app.domain.eligibility_rule_engine import check_eligibility, evaluate_rule
from app.models.scheme import RuleOperator, SchemeRule
from app.schemas.janmitra import PatientProfile


def make_profile(**overrides) -> PatientProfile:
    defaults = dict(
        age=30,
        gender="female",
        annual_income=100000,
        social_category="general",
        state="Maharashtra",
        is_bpl_card_holder=False,
        is_pregnant=False,
        has_disability=False,
    )
    defaults.update(overrides)
    return PatientProfile(**defaults)


def make_rule(field: str, operator: RuleOperator, value: str) -> SchemeRule:
    return SchemeRule(id=1, scheme_id=1, field=field, operator=operator, value=value)


class TestEvaluateRule:
    def test_lte_passes_when_income_below_threshold(self):
        profile = make_profile(annual_income=50000)
        rule = make_rule("annual_income", RuleOperator.LTE, "250000")
        result = evaluate_rule(profile, rule)
        assert result.passed is True

    def test_lte_fails_when_income_above_threshold(self):
        profile = make_profile(annual_income=500000)
        rule = make_rule("annual_income", RuleOperator.LTE, "250000")
        result = evaluate_rule(profile, rule)
        assert result.passed is False

    def test_boolean_rule(self):
        profile = make_profile(is_pregnant=True)
        rule = make_rule("is_pregnant", RuleOperator.EQ, "true")
        assert evaluate_rule(profile, rule).passed is True

    def test_in_operator_with_category_list(self):
        profile = make_profile(social_category="sc")
        rule = make_rule("social_category", RuleOperator.IN, "sc,st,obc")
        assert evaluate_rule(profile, rule).passed is True

        profile_general = make_profile(social_category="general")
        assert evaluate_rule(profile_general, rule).passed is False

    def test_none_optional_field_fails_closed_not_open(self):
        profile = make_profile(family_size=None)
        rule = make_rule("family_size", RuleOperator.GTE, "3")
        assert evaluate_rule(profile, rule).passed is False

    def test_unknown_field_raises_rule_engine_error(self):
        profile = make_profile()
        rule = make_rule("nonexistent_field", RuleOperator.EQ, "true")
        with pytest.raises(RuleEngineError):
            evaluate_rule(profile, rule)

    def test_malformed_stored_value_raises_rule_engine_error(self):
        profile = make_profile()
        rule = make_rule("annual_income", RuleOperator.LTE, "not-a-number")
        with pytest.raises(RuleEngineError):
            evaluate_rule(profile, rule)


class TestCheckEligibility:
    def test_all_rules_must_pass_for_eligibility(self):
        profile = make_profile(is_pregnant=True, gender="female")
        rules = [
            make_rule("is_pregnant", RuleOperator.EQ, "true"),
            make_rule("gender", RuleOperator.EQ, "female"),
        ]
        result = check_eligibility(profile, rules)
        assert result.is_eligible is True
        assert len(result.matched_rules) == 2
        assert result.failed_rules == []

    def test_single_failing_rule_makes_ineligible(self):
        profile = make_profile(is_pregnant=False)
        rules = [
            make_rule("is_pregnant", RuleOperator.EQ, "true"),
            make_rule("gender", RuleOperator.EQ, "female"),
        ]
        result = check_eligibility(profile, rules)
        assert result.is_eligible is False
        assert len(result.failed_rules) == 1

    def test_scheme_with_no_rules_is_ineligible_by_default(self):
        profile = make_profile()
        result = check_eligibility(profile, rules=[])
        assert result.is_eligible is False

    def test_same_input_always_produces_same_output_deterministic(self):
        profile = make_profile(annual_income=200000, is_bpl_card_holder=True)
        rules = [
            make_rule("annual_income", RuleOperator.LTE, "250000"),
            make_rule("is_bpl_card_holder", RuleOperator.EQ, "true"),
        ]
        results = [check_eligibility(profile, rules).is_eligible for _ in range(20)]
        assert all(r is True for r in results)
