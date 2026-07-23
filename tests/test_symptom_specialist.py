import numpy as np
from core.models import KeywordSymptomEncoder
from core.vector_store import InMemoryVectorStore, VectorStoreItem
from services.symptom_specialist.model import display_specialty, get_engine


def test_keyword_encoder_is_deterministic():
    encoder = KeywordSymptomEncoder(keywords=["chest pain", "cough"])

    first = encoder.encode(["chest pain and chest pain"], convert_to_numpy=True)
    second = encoder.encode(["chest pain and chest pain"], convert_to_numpy=True)

    np.testing.assert_array_equal(first, second)
    assert first.tolist() == [[2.0, 0.0]]


def test_vector_store_returns_cosine_ranked_neighbors():
    store = InMemoryVectorStore(
        [
            VectorStoreItem(vector=np.array([1.0, 0.0]), label="Cardiology"),
            VectorStoreItem(vector=np.array([0.0, 1.0]), label="Pulmonology"),
        ]
    )

    results = store.search(np.array([0.9, 0.1]), top_k=2)

    assert results[0][0] == "Cardiology"
    assert results[0][1] > results[1][1]


def test_symptom_engine_ranks_relevant_specialty():
    ranked, explanation = get_engine().rank_specialties(
        "chest pain with shortness of breath and high blood pressure",
        top_k=3,
    )

    assert ranked
    assert ranked[0].specialty == "Cardiology"
    assert "demo cases" in explanation


def test_display_specialty_normalizes_labels():
    assert display_specialty("allergy/immunology") == "Allergy/Immunology"
    assert display_specialty("gastroenterology") == "Gastroenterology"
