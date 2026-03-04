from typing import List, Optional

from pydantic import BaseModel


class SymptomSpecialistRequest(BaseModel):
    symptoms_text: str


class RankedSpecialty(BaseModel):
    specialty: str
    score: float


class SymptomSpecialistResponse(BaseModel):
    ranked_specialties: List[RankedSpecialty]
    explanation: Optional[str] = None


class SecondOpinionRequest(BaseModel):
    report_text: str


class SecondOpinionResponse(BaseModel):
    risk_level: str
    second_opinion_recommended: bool
    explanation: Optional[str] = None


class DrugInteractionsRequest(BaseModel):
    drugs: List[str]


class DrugInteractionPair(BaseModel):
    drug_a: str
    drug_b: str
    risk_level: str
    explanation: Optional[str] = None


class DrugInteractionsResponse(BaseModel):
    overall_risk: str
    interactions: List[DrugInteractionPair]

