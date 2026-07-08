"""
This module is the enforcement point for the platform's most important
safety rule: AI never determines eligibility. Nothing in this file imports
from `app.ai`, and nothing here calls an external model. Given a
PatientProfile and a scheme's stored SchemeRule rows, it returns a plain,
reproducible boolean plus the list of rules that matched/failed — the same
input always produces the same output, which is exactly what a government
eligibility decision needs to be.
"""

from dataclasses import dataclass
from typing import List

from app.core.exceptions import RuleEngineError
from app.models.scheme import RuleOperator, SchemeRule
from app.schemas.janmitra import FIELD_TYPES, PatientProfile

_OPERATORS = {
    RuleOperator.EQ: lambda a, b: a == b,
    RuleOperator.NEQ: lambda a, b: a != b,
    RuleOperator.LT: lambda a, b: a < b,
    RuleOperator.LTE: lambda a, b: a <= b,
    RuleOperator.GT: lambda a, b: a > b,
    RuleOperator.GTE: lambda a, b: a >= b,
    RuleOperator.IN: lambda a, b: a in b,
}


@dataclass
class RuleEvaluation:
    rule: SchemeRule
    passed: bool
    description: str


@dataclass
class EligibilityResult:
    is_eligible: bool
    matched_rules: List[str]
    failed_rules: List[str]


def _cast_value(field: str, raw_value: str, operator: RuleOperator):
    if field not in FIELD_TYPES:
        raise RuleEngineError(
            f"Scheme rule references unknown patient field '{field}'.",
            details={"field": field},
        )
    field_type = FIELD_TYPES[field]

    if operator == RuleOperator.IN:
        # Stored as a comma-separated list, e.g. "sc,st,obc"
        items = [item.strip() for item in raw_value.split(",")]
        if field_type is bool:
            return [item.lower() == "true" for item in items]
        if field_type in (int, float):
            return [field_type(item) for item in items]
        return items

    if field_type is bool:
        return raw_value.strip().lower() == "true"
    if field_type is int:
        return int(raw_value)
    if field_type is float:
        return float(raw_value)
    return raw_value


def evaluate_rule(profile: PatientProfile, rule: SchemeRule) -> RuleEvaluation:
    if not hasattr(profile, rule.field):
        raise RuleEngineError(
            f"Scheme rule references field '{rule.field}' which does not exist on PatientProfile.",
            details={"field": rule.field},
        )

    profile_value = getattr(profile, rule.field)
    try:
        comparison_value = _cast_value(rule.field, rule.value, rule.operator)
    except (ValueError, TypeError) as exc:
        raise RuleEngineError(
            f"Could not parse stored rule value '{rule.value}' for field '{rule.field}'.",
            details={"field": rule.field, "value": rule.value},
        ) from exc

    if profile_value is None:
        # A profile that doesn't specify an optional field can never satisfy
        # a rule that depends on it — fail closed, not open.
        passed = False
    else:
        comparator = _OPERATORS[rule.operator]
        passed = bool(comparator(profile_value, comparison_value))

    description = f"{rule.field} {rule.operator.value} {rule.value}"
    return RuleEvaluation(rule=rule, passed=passed, description=description)


def check_eligibility(profile: PatientProfile, rules: List[SchemeRule]) -> EligibilityResult:
    """A scheme with zero rules is treated as not configured for automated
    eligibility and is reported ineligible-by-default — we never grant
    eligibility in the absence of explicit, auditable rules."""
    if not rules:
        return EligibilityResult(is_eligible=False, matched_rules=[], failed_rules=["no eligibility rules configured"])

    evaluations = [evaluate_rule(profile, rule) for rule in rules]
    matched = [e.description for e in evaluations if e.passed]
    failed = [e.description for e in evaluations if not e.passed]
    is_eligible = all(e.passed for e in evaluations)

    return EligibilityResult(is_eligible=is_eligible, matched_rules=matched, failed_rules=failed)
