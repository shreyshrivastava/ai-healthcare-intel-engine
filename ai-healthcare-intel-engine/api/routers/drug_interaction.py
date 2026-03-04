from typing import List

from fastapi import APIRouter

from api.schemas import DrugInteractionsRequest, DrugInteractionsResponse
from services.drug_interaction.inference import (
    check_interactions,
    overall_risk_from_pairs,
    to_schema_pairs,
)


router = APIRouter()


@router.post("/check", response_model=DrugInteractionsResponse)
async def check_drug_interactions(payload: DrugInteractionsRequest) -> DrugInteractionsResponse:
    drugs: List[str] = payload.drugs
    results = check_interactions(drugs)
    pairs = to_schema_pairs(results)
    overall_risk = overall_risk_from_pairs(results)
    return DrugInteractionsResponse(overall_risk=overall_risk, interactions=pairs)

