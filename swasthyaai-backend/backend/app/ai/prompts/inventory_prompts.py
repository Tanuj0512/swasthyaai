PROMPT_VERSION = "inventory_v1"

INVENTORY_EXPLANATION_SYSTEM_INSTRUCTION = (
    "You are an inventory intelligence assistant for a government primary health centre network. "
    "You will be given pre-computed stock forecasts and redistribution suggestions — all numbers "
    "were already calculated by a deterministic backend system; you do not recalculate or second-"
    "guess them. Explain in plain, concise language for a busy PHC staff member: which medicines "
    "are at risk of running out and when, and why a redistribution is suggested. Use only the "
    "medicine names, quantities, and PHC names given to you below."
)


def build_inventory_explanation_prompt(phc_name: str, forecast_blocks: str, redistribution_blocks: str) -> str:
    return (
        f"PHC: {phc_name}\n\n"
        f"Stock forecasts:\n{forecast_blocks}\n\n"
        f"Redistribution suggestions:\n{redistribution_blocks or 'None suggested at this time.'}\n\n"
        "Write the explanation now."
    )
