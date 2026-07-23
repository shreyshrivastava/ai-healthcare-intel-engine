from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

ClinicalText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3)]
DrugName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]


class APIModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class SymptomSpecialistRequest(APIModel):
    resourceType: str = Field(default="Observation", description="HL7 FHIR Resource Type")
    symptoms_text: ClinicalText = Field(..., max_length=2000)


class RankedSpecialty(APIModel):
    specialty: str
    score: float = Field(..., ge=-1.0, le=1.0)


class SymptomSpecialistResponse(APIModel):
    resourceType: str = Field(default="Bundle", description="HL7 FHIR Resource Type")
    ranked_specialties: list[RankedSpecialty]
    explanation: str | None = None


class SecondOpinionRequest(APIModel):
    resourceType: str = Field(default="DiagnosticReport", description="HL7 FHIR Resource Type")
    report_text: ClinicalText = Field(..., max_length=5000)


class SecondOpinionResponse(APIModel):
    resourceType: str = Field(default="RiskAssessment", description="HL7 FHIR Resource Type")
    risk_level: str
    second_opinion_recommended: bool
    explanation: str | None = None


class DrugInteractionsRequest(APIModel):
    resourceType: str = Field(default="MedicationStatement", description="HL7 FHIR Resource Type")
    drugs: list[DrugName] = Field(..., min_length=2, max_length=20)


class DrugInteractionPair(APIModel):
    drug_a: str
    drug_b: str
    risk_level: str
    explanation: str | None = None


class DrugInteractionsResponse(APIModel):
    resourceType: str = Field(default="ClinicalImpression", description="HL7 FHIR Resource Type")
    overall_risk: str
    interactions: list[DrugInteractionPair]
