import hashlib
import re
from typing import List, Optional

from fastapi import BackgroundTasks
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai.guardrails import FALLBACK_MESSAGE, validate_input
from app.ai.orchestrator import AIOrchestrator
from app.ai.prompts.janmitra_prompts import (
    CITIZEN_QUERY_SYSTEM_INSTRUCTION,
    ELIGIBILITY_EXPLANATION_SYSTEM_INSTRUCTION,
    EXTRACTION_JSON_SCHEMA,
    EXTRACTION_SYSTEM_INSTRUCTION,
    PROMPT_VERSION,
    build_citizen_query_prompt,
    build_eligibility_explanation_prompt,
)
from app.background.tasks import log_ai_interaction, log_eligibility_check
from app.core.exceptions import GuardrailViolationError
from app.domain.eligibility_rule_engine import check_eligibility
from app.repositories.scheme_repository import SchemeRepository, SchemeRuleRepository
from app.schemas.common import AIExplanation
from app.schemas.janmitra import (
    CitizenQueryResponse,
    EligibilityCheckResponse,
    ExtractProfileResponse,
    PatientProfile,
    SchemeDocumentOut,
    SchemeEligibilityResult,
    SchemeOut,
)

_STOPWORDS = {
    "what", "which", "where", "when", "does", "have", "with", "this", "that", "your",
    "there", "about", "scheme", "schemes", "eligible", "eligibility", "please", "know",
    "want", "need", "list", "show",
}


def _scheme_to_out(scheme) -> SchemeOut:
    return SchemeOut(
        id=scheme.id,
        name=scheme.name,
        level=scheme.level.value,
        authority=scheme.authority,
        description=scheme.description,
        benefits_summary=scheme.benefits_summary,
        official_url=scheme.official_url,
        documents=[SchemeDocumentOut(document_name=d.document_name, mandatory=d.mandatory) for d in scheme.documents],
    )


def _scheme_block(scheme) -> str:
    docs = ", ".join(d.document_name for d in scheme.documents) or "None specified"
    return (
        f"- Scheme: {scheme.name} ({scheme.level.value}, {scheme.authority})\n"
        f"  Description: {scheme.description}\n"
        f"  Benefits: {scheme.benefits_summary}\n"
        f"  Required documents: {docs}"
    )


class JanMitraService:
    def __init__(self, db: Session, orchestrator: Optional[AIOrchestrator] = None):
        self.db = db
        self.scheme_repo = SchemeRepository(db)
        self.rule_repo = SchemeRuleRepository(db)
        self.orchestrator = orchestrator or AIOrchestrator()

    def list_schemes(self) -> List[SchemeOut]:
        return [_scheme_to_out(s) for s in self.scheme_repo.list_active()]

    def extract_profile(self, free_text: str) -> ExtractProfileResponse:
        validated_text = validate_input(free_text)

        raw = self.orchestrator.extract_structured(
            system_instruction_base=EXTRACTION_SYSTEM_INSTRUCTION,
            user_prompt=validated_text,
            json_schema=EXTRACTION_JSON_SCHEMA,
        )
        try:
            profile = PatientProfile.model_validate(raw)
        except ValidationError as exc:
            raise GuardrailViolationError(
                "The extracted patient profile was incomplete or invalid. "
                "Please provide age, gender, income, category, and state explicitly.",
                details=exc.errors(),
            ) from exc

        return ExtractProfileResponse(profile=profile, provider=self.orchestrator.get_active_provider_name())

    def check_eligibility(
        self,
        profile: PatientProfile,
        phc_id: Optional[int],
        checked_by_role: str,
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> EligibilityCheckResponse:
        schemes = self.scheme_repo.list_active()
        results: List[SchemeEligibilityResult] = []
        eligible_schemes = []

        for scheme in schemes:
            rules = self.rule_repo.list_for_scheme(scheme.id)
            outcome = check_eligibility(profile, rules)
            results.append(
                SchemeEligibilityResult(
                    scheme=_scheme_to_out(scheme),
                    is_eligible=outcome.is_eligible,
                    matched_rules=outcome.matched_rules,
                    failed_rules=outcome.failed_rules,
                )
            )
            if background_tasks is not None:
                background_tasks.add_task(
                    log_eligibility_check,
                    phc_id=phc_id,
                    scheme_id=scheme.id,
                    is_eligible=outcome.is_eligible,
                    checked_by_role=checked_by_role,
                )
            if outcome.is_eligible:
                eligible_schemes.append(scheme)

        if not eligible_schemes:
            explanation = AIExplanation(
                text="Based on the profile provided, no configured scheme matched the eligibility rules.",
                provider="fallback_template",
                grounded=True,
            )
            return EligibilityCheckResponse(results=results, explanation=explanation)

        scheme_blocks = "\n".join(_scheme_block(s) for s in eligible_schemes)
        fallback_text = "You may be eligible for:\n" + "\n".join(
            f"- {s.name}: {s.benefits_summary}" for s in eligible_schemes
        )

        result = self.orchestrator.generate_grounded_explanation(
            system_instruction_base=ELIGIBILITY_EXPLANATION_SYSTEM_INSTRUCTION,
            user_prompt=build_eligibility_explanation_prompt(
                "Explain eligibility results to the patient/staff member.", scheme_blocks
            ),
            grounding_terms=[s.name for s in eligible_schemes],
            fallback_text=fallback_text,
        )

        input_hash = hashlib.sha256(scheme_blocks.encode()).hexdigest()
        if background_tasks is not None:
            background_tasks.add_task(
                log_ai_interaction,
                module="janmitra_eligibility",
                provider_used=result.provider,
                prompt_template_version=PROMPT_VERSION,
                input_hash=input_hash,
                output_summary=result.text,
                guardrail_flags=result.guardrail_flags,
                succeeded=result.succeeded,
            )

        return EligibilityCheckResponse(
            results=results,
            explanation=AIExplanation(text=result.text, provider=result.provider, grounded=result.grounded),
        )

    def citizen_query(self, question: str, language: str, background_tasks: Optional[BackgroundTasks] = None) -> CitizenQueryResponse:
        validated_question = validate_input(question)

        words = re.findall(r"[a-zA-Z]{4,}", validated_question.lower())
        keywords = [w for w in words if w not in _STOPWORDS]

        matched_schemes = self.scheme_repo.search(keywords)

        if not matched_schemes:
            explanation = AIExplanation(text=FALLBACK_MESSAGE, provider="fallback_template", grounded=True)
            return CitizenQueryResponse(matched_schemes=[], explanation=explanation)

        scheme_blocks = "\n".join(_scheme_block(s) for s in matched_schemes)
        fallback_text = "Here is what I found:\n" + "\n".join(
            f"- {s.name}: {s.benefits_summary}" for s in matched_schemes
        )

        result = self.orchestrator.generate_grounded_explanation(
            system_instruction_base=CITIZEN_QUERY_SYSTEM_INSTRUCTION,
            user_prompt=build_citizen_query_prompt(validated_question, scheme_blocks),
            grounding_terms=[s.name for s in matched_schemes],
            fallback_text=fallback_text,
        )

        input_hash = hashlib.sha256(validated_question.encode()).hexdigest()
        if background_tasks is not None:
            background_tasks.add_task(
                log_ai_interaction,
                module="janmitra_citizen_query",
                provider_used=result.provider,
                prompt_template_version=PROMPT_VERSION,
                input_hash=input_hash,
                output_summary=result.text,
                guardrail_flags=result.guardrail_flags,
                succeeded=result.succeeded,
            )

        return CitizenQueryResponse(
            matched_schemes=[_scheme_to_out(s) for s in matched_schemes],
            explanation=AIExplanation(text=result.text, provider=result.provider, grounded=result.grounded),
        )
