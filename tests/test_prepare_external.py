from services.drug_interaction.prepare_external_ddi import normalize_risk
from services.second_opinion.prepare_external_risk import normalize_label
from services.symptom_specialist.prepare_external_symptoms import normalize_specialty


def test_external_data_normalizers():
    assert normalize_specialty("cardio") == "Cardiology"
    assert normalize_label("complex") == "High"
    assert normalize_risk("major") == "High"
    assert normalize_risk("minor") == "Low"
