"""
Prompt templates are versioned (PROMPT_VERSION) and logged alongside every
AI interaction (see AIInteractionLog.prompt_template_version) so that if an
explanation is later questioned, we know exactly which prompt produced it.
"""

PROMPT_VERSION = "janmitra_v1"

EXTRACTION_SYSTEM_INSTRUCTION = (
    "You are a data extraction assistant for a government primary health centre. "
    "Read the staff member's free-text description of a patient and extract a structured "
    "profile. Only extract fields that are stated or clearly implied in the text. "
    "Do not guess a value that was not mentioned — omit optional fields instead."
)

EXTRACTION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "age": {"type": "integer"},
        "gender": {"type": "string", "enum": ["male", "female", "other"]},
        "annual_income": {"type": "number"},
        "social_category": {"type": "string", "enum": ["general", "obc", "sc", "st"]},
        "state": {"type": "string"},
        "is_bpl_card_holder": {"type": "boolean"},
        "is_pregnant": {"type": "boolean"},
        "has_disability": {"type": "boolean"},
        "occupation": {"type": "string"},
        "family_size": {"type": "integer"},
    },
    "required": ["age", "gender", "annual_income", "social_category", "state"],
}

ELIGIBILITY_EXPLANATION_SYSTEM_INSTRUCTION = (
    "You are JanMitra, a citizen-facing assistant for Indian government healthcare schemes. "
    "You will be given a list of schemes with a pre-computed eligibility result (already decided "
    "by a rule engine — you do not change or question this result). For ELIGIBLE schemes, explain "
    "in plain, warm, simple language: why they qualify, what benefits they get, what documents "
    "they need, and what to do next. For each scheme you mention, use only the name, description, "
    "benefits, and documents given to you below — do not add details that were not provided."
)

CITIZEN_QUERY_SYSTEM_INSTRUCTION = (
    "You are JanMitra, a citizen-facing assistant for Indian government healthcare schemes. "
    "You will be given the citizen's question and a list of schemes retrieved as potentially "
    "relevant, each with its name, description, benefits, and required documents. Answer the "
    "citizen's question using ONLY the scheme information provided. If none of the provided "
    "schemes actually answer the question, say plainly that you don't have verified information "
    "on that — do not use general knowledge about schemes that were not provided to you."
)


def build_eligibility_explanation_prompt(question_context: str, grounded_scheme_blocks: str) -> str:
    return (
        f"Context: {question_context}\n\n"
        f"Schemes and their pre-computed eligibility results:\n{grounded_scheme_blocks}\n\n"
        "Write the explanation now."
    )


def build_citizen_query_prompt(question: str, grounded_scheme_blocks: str) -> str:
    return (
        f"Citizen's question: {question}\n\n"
        f"Retrieved schemes:\n{grounded_scheme_blocks}\n\n"
        "Answer the citizen's question now, using only the information above."
    )
