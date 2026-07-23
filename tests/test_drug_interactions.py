from services.drug_interaction.inference import (
    canonicalize_drug_name,
    check_interactions,
    overall_risk_from_pairs,
)


def test_detects_known_high_risk_interaction():
    results = check_interactions(["warfarin", "aspirin"])

    assert len(results) == 1
    assert results[0].risk_level == "High"
    assert overall_risk_from_pairs(results) == "High"


def test_detects_reversed_interaction_order():
    results = check_interactions(["clarithromycin", "simvastatin"])

    assert len(results) == 1
    assert results[0].risk_level == "High"


def test_alias_normalization_supports_demo_lookup():
    assert canonicalize_drug_name("nitrates") == "nitroglycerin"

    results = check_interactions(["sildenafil", "nitrates"])

    assert len(results) == 1
    assert results[0].drug_b == "nitrates"
    assert results[0].risk_level == "High"


def test_unknown_or_duplicate_drugs_do_not_create_false_interactions():
    results = check_interactions(["metformin", "metformin", "amoxicillin"])

    assert results == []
    assert overall_risk_from_pairs(results) == "None"
