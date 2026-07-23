from services.second_opinion.model import assess_report_text


def test_high_risk_report_recommends_second_opinion():
    prediction = assess_report_text(
        "Patient admitted to ICU with septic shock requiring ventilator support."
    )

    assert prediction.risk_level == "High"
    assert prediction.second_opinion_recommended is True
    assert "septic shock" in prediction.contributing_phrases


def test_negated_high_risk_phrase_does_not_trigger_high_risk():
    prediction = assess_report_text(
        "Uncomplicated urinary tract infection responding to oral antibiotics with no ICU care."
    )

    assert prediction.risk_level == "Low"
    assert prediction.second_opinion_recommended is False


def test_medium_risk_report_recommends_second_opinion():
    prediction = assess_report_text(
        "Patient has acute kidney injury with creatinine elevation and multiple comorbidities."
    )

    assert prediction.risk_level == "Medium"
    assert prediction.second_opinion_recommended is True
