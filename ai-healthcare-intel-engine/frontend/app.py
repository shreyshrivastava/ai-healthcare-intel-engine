import os
import sys
from pathlib import Path
from typing import Any

import requests
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.drug_interaction.inference import (  # noqa: E402
    check_interactions,
    overall_risk_from_pairs,
    to_schema_pairs,
)
from services.second_opinion.model import assess_report_text  # noqa: E402
from services.symptom_specialist.retriever import predict_ranked_specialties  # noqa: E402

API_URL = os.getenv("API_URL", "").rstrip("/")
FRONTEND_MODE = os.getenv("HEALTHCARE_FRONTEND_MODE", "local").strip().lower()
REQUEST_TIMEOUT_SECONDS = float(os.getenv("API_TIMEOUT_SECONDS", "15"))


def api_mode_enabled() -> bool:
    return FRONTEND_MODE == "api" and bool(API_URL)


def post_api(endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(
        f"{API_URL}{endpoint}",
        json=payload,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def predict_specialties(symptoms_text: str) -> dict[str, Any]:
    if api_mode_enabled():
        return post_api("/symptom-specialist/predict", {"symptoms_text": symptoms_text})

    ranked = predict_ranked_specialties(symptoms_text)
    return {
        "ranked_specialties": [item.model_dump() for item in ranked],
        "explanation": "Ranked locally with the deterministic demo encoder.",
    }


def assess_risk(report_text: str) -> dict[str, Any]:
    if api_mode_enabled():
        return post_api("/second-opinion/assess", {"report_text": report_text})

    prediction = assess_report_text(report_text)
    phrases = ", ".join(f"'{phrase}'" for phrase in prediction.contributing_phrases)
    explanation = (
        f"Risk level inferred from phrases: {phrases}."
        if phrases
        else "No explicit high- or medium-risk phrases detected in the report."
    )
    return {
        "risk_level": prediction.risk_level,
        "second_opinion_recommended": prediction.second_opinion_recommended,
        "explanation": explanation,
    }


def check_drugs(drugs: list[str]) -> dict[str, Any]:
    if api_mode_enabled():
        return post_api("/drug-interactions/check", {"drugs": drugs})

    results = check_interactions(drugs)
    return {
        "overall_risk": overall_risk_from_pairs(results),
        "interactions": [item.model_dump() for item in to_schema_pairs(results)],
    }


def render_request_error(exc: Exception) -> None:
    st.error(f"Unable to complete the demo request: {exc}")


st.set_page_config(page_title="AI Healthcare Intelligence Engine", layout="wide")

st.title("AI Healthcare Intelligence Engine")
st.caption("Clinical decision-support demo for synthetic scenarios. Not medical advice.")
st.warning(
    "Do not enter real patient identifiers or protected health information. "
    "This portfolio demo uses heuristic and synthetic data only."
)


tab1, tab2, tab3 = st.tabs(
    ["🧑‍⚕️ Symptom → Specialist", "📝 Second Opinion Risk", "💊 Drug Interactions"]
)


with tab1:
    st.subheader("Symptom to Specialist Matching")
    symptoms_text = st.text_area(
        "Describe symptoms",
        height=160,
        placeholder="Example: chest pain on exertion with shortness of breath",
    )
    if st.button("Predict Specialist", key="predict_specialist"):
        if not symptoms_text.strip():
            st.warning("Please enter symptoms text.")
        else:
            try:
                data = predict_specialties(symptoms_text)
                st.write("### Ranked Specialties")
                for item in data["ranked_specialties"]:
                    st.write(f"- **{item['specialty']}** — score: `{item['score']:.2f}`")
                if data.get("explanation"):
                    st.info(data["explanation"])
            except Exception as exc:
                render_request_error(exc)


with tab2:
    st.subheader("Second Opinion Risk Stratifier")
    report_text = st.text_area(
        "Paste de-identified diagnosis summary or report",
        height=200,
        placeholder="Example: Patient admitted to ICU with septic shock...",
    )
    if st.button("Assess Risk", key="assess_risk"):
        if not report_text.strip():
            st.warning("Please paste a report.")
        else:
            try:
                data = assess_risk(report_text)
                st.write(f"### Risk Level: **{data['risk_level']}**")
                st.write(
                    f"Second opinion recommended: "
                    f"**{'Yes' if data['second_opinion_recommended'] else 'No'}**"
                )
                if data.get("explanation"):
                    st.info(data["explanation"])
            except Exception as exc:
                render_request_error(exc)


with tab3:
    st.subheader("Drug Interaction Intelligence")
    drugs_input = st.text_area(
        "List drugs (one per line or comma-separated)", height=160, placeholder="warfarin\naspirin"
    )
    if st.button("Check Interactions", key="check_interactions"):
        raw = drugs_input.replace(",", "\n")
        drugs = [d.strip() for d in raw.splitlines() if d.strip()]
        if not drugs:
            st.warning("Please enter at least two drugs.")
        elif len(drugs) < 2:
            st.warning("Please enter at least two drugs.")
        else:
            try:
                data = check_drugs(drugs)
                st.write(f"### Overall regimen risk: **{data['overall_risk']}**")
                if data["interactions"]:
                    st.write("### Detected interactions")
                    for pair in data["interactions"]:
                        st.write(
                            f"- **{pair['drug_a']} + {pair['drug_b']}** — "
                            f"risk: **{pair['risk_level']}**"
                        )
                        if pair.get("explanation"):
                            st.caption(pair["explanation"])
                else:
                    st.success("No interactions detected in the current demo knowledge graph.")
            except Exception as exc:
                render_request_error(exc)
