from __future__ import annotations

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

SYMPTOM_SAMPLES = {
    "Cardiology": "pressure-like chest pain with shortness of breath and elevated blood pressure",
    "Pulmonology": "wheezing cough and difficulty breathing that worsens at night",
    "Neurology": "headaches dizziness vision problems and numbness in the feet",
    "Urology": "flank pain blood in urine and painful urination",
}

RISK_SAMPLES = {
    "High risk": "Patient with septic shock on vasopressors and ventilator support in ICU.",
    "Medium risk": "Acute kidney injury with creatinine elevation after dehydration.",
    "Low risk": "Minor laceration closed with sutures and no sign of infection.",
}

DRUG_SAMPLES = {
    "High interaction": "warfarin\naspirin",
    "Alias interaction": "nitrates\nsildenafil",
    "No known interaction": "metformin\namoxicillin",
}


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


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .stApp { background: #f7f8fb; color: #17202a; }
        .block-container { max-width: 1180px; padding-top: 2rem; }
        .hero {
            border-bottom: 1px solid #d9e2ec;
            padding: 10px 0 18px;
            margin-bottom: 18px;
        }
        .hero h1 { font-size: 30px; margin: 0 0 6px; letter-spacing: 0; color: #102a43; }
        .hero p { color: #52606d; margin: 0; line-height: 1.5; }
        .status-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }
        .status-pill {
            border: 1px solid #bcccdc;
            border-radius: 999px;
            padding: 5px 10px;
            color: #334e68;
            background: #f0f4f8;
            font-size: 13px;
        }
        .risk-high { color: #b42318; font-weight: 700; }
        .risk-medium { color: #a15c07; font-weight: 700; }
        .risk-low, .risk-none { color: #027a48; font-weight: 700; }
        div.stButton > button { border-radius: 6px; font-weight: 600; }
        [data-testid="stMetricValue"] { color: #102a43; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    mode_label = "API mode" if api_mode_enabled() else "Standalone mode"
    st.markdown(
        f"""
        <div class="hero">
            <h1>AI Healthcare Intelligence Engine</h1>
            <p>Clinical decision-support demo for synthetic scenarios: route symptoms, triage second-opinion risk, and inspect drug interaction edges.</p>
            <div class="status-row">
                <span class="status-pill">{mode_label}</span>
                <span class="status-pill">Synthetic data only</span>
                <span class="status-pill">Not medical advice</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    st.sidebar.header("Demo Configuration")
    st.sidebar.write(f"Frontend mode: `{FRONTEND_MODE}`")
    st.sidebar.write(f"Embedding backend: `{os.getenv('HEALTHCARE_EMBEDDING_BACKEND', 'keyword')}`")
    if api_mode_enabled():
        st.sidebar.write(f"API URL: `{API_URL}`")
    else:
        st.sidebar.write("API URL: `not required`")
    st.sidebar.divider()
    st.sidebar.caption(
        "Use de-identified synthetic examples only. This app is for portfolio demonstration, not diagnosis or treatment."
    )


def render_request_error(exc: Exception) -> None:
    st.error(f"Unable to complete the demo request: {exc}")


def render_specialty_results(data: dict[str, Any]) -> None:
    ranked = data["ranked_specialties"]
    top = ranked[0] if ranked else {"specialty": "No match", "score": 0.0}
    with st.container(border=True):
        st.metric("Top Specialty", top["specialty"], f"{top['score']:.2f} similarity")
        for item in ranked:
            score = max(0.0, min(1.0, float(item["score"])))
            st.write(f"**{item['specialty']}**")
            st.progress(score)
        if data.get("explanation"):
            st.info(data["explanation"])


def render_risk_results(data: dict[str, Any]) -> None:
    risk = data["risk_level"]
    css_class = f"risk-{risk.lower()}"
    with st.container(border=True):
        col1, col2 = st.columns(2)
        col1.metric("Risk Level", risk)
        col2.metric(
            "Second Opinion", "Recommended" if data["second_opinion_recommended"] else "Not flagged"
        )
        st.markdown(f'<p class="{css_class}">Risk tier: {risk}</p>', unsafe_allow_html=True)
        if data.get("explanation"):
            st.info(data["explanation"])


def render_drug_results(data: dict[str, Any]) -> None:
    risk = data["overall_risk"]
    css_class = f"risk-{risk.lower()}"
    with st.container(border=True):
        st.metric("Overall Regimen Risk", risk)
        st.markdown(
            f'<p class="{css_class}">Detected regimen risk: {risk}</p>', unsafe_allow_html=True
        )
        if data["interactions"]:
            for pair in data["interactions"]:
                st.write(f"**{pair['drug_a']} + {pair['drug_b']}**")
                st.caption(
                    f"{pair['risk_level']}: {pair.get('explanation') or 'No mechanism provided.'}"
                )
        else:
            st.success("No interactions detected in the current demo knowledge graph.")


st.set_page_config(page_title="AI Healthcare Intelligence Engine", layout="wide")
inject_css()
render_header()
render_sidebar()

tab1, tab2, tab3 = st.tabs(["Symptom Routing", "Second-Opinion Risk", "Drug Interactions"])

with tab1:
    st.subheader("Symptom to Specialist Routing")
    sample = st.selectbox("Load sample", list(SYMPTOM_SAMPLES), key="symptom_sample")
    symptoms_text = st.text_area(
        "Describe symptoms",
        value=SYMPTOM_SAMPLES[sample],
        height=150,
        placeholder="Example: chest pain on exertion with shortness of breath",
    )
    if st.button("Predict Specialty", key="predict_specialist", type="primary"):
        if not symptoms_text.strip():
            st.warning("Please enter symptoms text.")
        else:
            try:
                render_specialty_results(predict_specialties(symptoms_text))
            except Exception as exc:
                render_request_error(exc)

with tab2:
    st.subheader("Second-Opinion Risk Stratifier")
    sample = st.selectbox("Load sample", list(RISK_SAMPLES), key="risk_sample")
    report_text = st.text_area(
        "Paste de-identified diagnosis summary or report",
        value=RISK_SAMPLES[sample],
        height=170,
    )
    if st.button("Assess Risk", key="assess_risk", type="primary"):
        if not report_text.strip():
            st.warning("Please paste a report.")
        else:
            try:
                render_risk_results(assess_risk(report_text))
            except Exception as exc:
                render_request_error(exc)

with tab3:
    st.subheader("Drug Interaction Intelligence")
    sample = st.selectbox("Load sample", list(DRUG_SAMPLES), key="drug_sample")
    drugs_input = st.text_area(
        "List drugs, one per line or comma-separated",
        value=DRUG_SAMPLES[sample],
        height=150,
        placeholder="warfarin\naspirin",
    )
    if st.button("Check Interactions", key="check_interactions", type="primary"):
        drugs = [
            drug.strip() for drug in drugs_input.replace(",", "\n").splitlines() if drug.strip()
        ]
        if len(drugs) < 2:
            st.warning("Please enter at least two drugs.")
        else:
            try:
                render_drug_results(check_drugs(drugs))
            except Exception as exc:
                render_request_error(exc)
