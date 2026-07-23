from api.main import create_app
from fastapi.testclient import TestClient

client = TestClient(create_app())


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_endpoint_tracks_requests():
    client.get("/health")
    response = client.get("/metrics")

    assert response.status_code == 200
    data = response.json()
    assert data["request_count"] >= 1
    assert "GET /health" in data["paths"]


def test_symptom_specialist_endpoint():
    response = client.post(
        "/symptom-specialist/predict",
        json={"symptoms_text": "chest pain and shortness of breath"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ranked_specialties"][0]["specialty"] == "Cardiology"


def test_second_opinion_endpoint():
    response = client.post(
        "/second-opinion/assess",
        json={"report_text": "Acute pulmonary embolism with right heart strain."},
    )

    assert response.status_code == 200
    assert response.json()["risk_level"] == "High"


def test_drug_interactions_endpoint():
    response = client.post(
        "/drug-interactions/check",
        json={"drugs": ["warfarin", "aspirin"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["overall_risk"] == "High"
    assert data["interactions"]


def test_validation_rejects_empty_symptoms():
    response = client.post("/symptom-specialist/predict", json={"symptoms_text": ""})

    assert response.status_code == 422


def test_validation_rejects_single_drug():
    response = client.post("/drug-interactions/check", json={"drugs": ["warfarin"]})

    assert response.status_code == 422
