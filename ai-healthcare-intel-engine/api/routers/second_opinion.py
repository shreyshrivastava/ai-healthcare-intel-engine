from fastapi import APIRouter

from api.schemas import SecondOpinionRequest, SecondOpinionResponse
from services.second_opinion.model import assess_report_text


router = APIRouter()


@router.post("/assess", response_model=SecondOpinionResponse)
async def assess_second_opinion(payload: SecondOpinionRequest) -> SecondOpinionResponse:
    prediction = assess_report_text(payload.report_text)
    if prediction.contributing_phrases:
        phrases = ", ".join(f"'{p}'" for p in prediction.contributing_phrases)
        explanation = f"Risk level inferred from phrases: {phrases}."
    else:
        explanation = "No explicit high- or medium-risk phrases detected in the report."

    return SecondOpinionResponse(
        risk_level=prediction.risk_level,
        second_opinion_recommended=prediction.second_opinion_recommended,
        explanation=explanation,
    )

