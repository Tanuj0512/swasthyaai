from typing import Dict, List, Literal, Optional, Type

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.common import AIExplanation


class PatientProfile(BaseModel):
    """
    The ONLY structured representation of a patient the system uses to
    determine eligibility. Produced either by direct staff form entry or by
    AI extraction from free text (see JanMitraService.extract_profile) — in
    both cases it passes through this same Pydantic validation before ever
    reaching the rule engine. Field names here are exactly what
    `SchemeRule.field` values reference; `FIELD_TYPES` below is the contract
    the rule engine uses to safely parse each rule's stored string `value`.
    """

    age: int = Field(..., ge=0, le=120)
    gender: Literal["male", "female", "other"]
    annual_income: float = Field(..., ge=0)
    social_category: Literal["general", "obc", "sc", "st"]
    state: str
    is_bpl_card_holder: bool = False
    is_pregnant: bool = False
    has_disability: bool = False
    occupation: Optional[str] = None
    family_size: Optional[int] = Field(default=None, ge=1)


FIELD_TYPES: Dict[str, Type] = {
    "age": int,
    "gender": str,
    "annual_income": float,
    "social_category": str,
    "state": str,
    "is_bpl_card_holder": bool,
    "is_pregnant": bool,
    "has_disability": bool,
    "occupation": str,
    "family_size": int,
}


class ExtractProfileRequest(BaseModel):
    free_text: str = Field(..., min_length=5, max_length=2000)


class ExtractProfileResponse(BaseModel):
    profile: PatientProfile
    provider: str
    extraction_confidence_note: str = (
        "Extracted by AI from free text. Please verify all fields with the patient before proceeding."
    )


class SchemeDocumentOut(BaseModel):
    document_name: str
    mandatory: bool

    model_config = ConfigDict(from_attributes=True)


class SchemeOut(BaseModel):
    id: int
    name: str
    level: str
    authority: str
    description: str
    benefits_summary: str
    official_url: Optional[str] = None
    documents: List[SchemeDocumentOut] = []

    model_config = ConfigDict(from_attributes=True)


class EligibilityCheckRequest(BaseModel):
    profile: PatientProfile
    phc_id: Optional[int] = None


class SchemeEligibilityResult(BaseModel):
    scheme: SchemeOut
    is_eligible: bool
    matched_rules: List[str]
    failed_rules: List[str]


class EligibilityCheckResponse(BaseModel):
    results: List[SchemeEligibilityResult]
    explanation: AIExplanation


class CitizenQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    language: Literal["en", "hi"] = "en"


class CitizenQueryResponse(BaseModel):
    matched_schemes: List[SchemeOut]
    explanation: AIExplanation
