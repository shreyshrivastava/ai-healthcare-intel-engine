from api.schemas import SymptomSpecialistRequest, SymptomSpecialistResponse
from fastapi import APIRouter
from services.symptom_specialist.retriever import predict_ranked_specialties

router = APIRouter()


@router.post("/predict", response_model=SymptomSpecialistResponse)
def predict_specialist(payload: SymptomSpecialistRequest) -> SymptomSpecialistResponse:
    ranked = predict_ranked_specialties(payload.symptoms_text)
    explanation = (
        "Ranked using a sentence-transformer encoder over a small demo corpus. "
        "Scores reflect embedding similarity to historical-like cases."
    )
    return SymptomSpecialistResponse(ranked_specialties=ranked, explanation=explanation)
