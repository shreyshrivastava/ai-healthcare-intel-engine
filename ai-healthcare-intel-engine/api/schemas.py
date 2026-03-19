from typing import List, Optional

from pydantic import BaseModel, Field


class SymptomSpecialistRequest(BaseModel):
    resourceType: str = Field(default="Observation", description="HL7 FHIR Resource Type")
    symptoms_text: str


class RankedSpecialty(BaseModel):
    specialty: str
    score: float


class SymptomSpecialistResponse(BaseModel):
    resourceType: str = Field(default="Bundle", description="HL7 FHIR Resource Type")
    ranked_specialties: List[RankedSpecialty]
    explanation: Optional[str] = None


class SecondOpinionRequest(BaseModel):
    resourceType: str = Field(default="DiagnosticReport", description="HL7 FHIR Resource Type")
    report_text: str


class SecondOpinionResponse(BaseModel):
    resourceType: str = Field(default="RiskAssessment", description="HL7 FHIR Resource Type")
    risk_level: str
    second_opinion_recommended: bool
    explanation: Optional[str] = None


class DrugInteractionsRequest(BaseModel):
    resourceType: str = Field(default="MedicationStatement", description="HL7 FHIR Resource Type")
    drugs: List[str]


class DrugInteractionPair(BaseModel):
    drug_a: str
    drug_b: str
    risk_level: str
    explanation: Optional[str] = None


class DrugInteractionsResponse(BaseModel):
    resourceType: str = Field(default="ClinicalImpression", description="HL7 FHIR Resource Type")
    overall_risk: str
    interactions: List[DrugInteractionPair]
