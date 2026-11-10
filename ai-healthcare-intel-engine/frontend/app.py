from __future__ import annotations

import html
import os
import sys
from pathlib import Path
from typing import Any

import requests
import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = FRONTEND_DIR.parent
REPO_URL = "https://github.com/shreyshrivastava/ai-healthcare-intel-engine"
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


RISK_KEYS = {"high", "medium", "low", "none"}


def risk_key(risk: str) -> str:
    """Map a risk label to a known CSS class, whatever the API returned."""
    key = str(risk).strip().lower()
    return key if key in RISK_KEYS else "none"


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def parse_drugs(text: str) -> list[str]:
    return [drug.strip() for drug in text.replace(",", "\n").splitlines() if drug.strip()]


def report(title: str, body: str, basis: str = "") -> str:
    footer = f'<div class="basis"><b>Basis:</b> {esc(basis)}</div>' if basis else ""
    return (
        f'<section class="report"><div class="report-head">{esc(title)}</div>'
        f'<div class="report-body">{body}</div>{footer}</section>'
    )


def specialty_slip(data: dict[str, Any]) -> str:
    ranked = data["ranked_specialties"]
    has_match = bool(ranked) and float(ranked[0]["score"]) > 0
    verdict = esc(ranked[0]["specialty"]) if has_match else "No clear match"
    rows = ""
    for item in ranked:
        score = max(0.0, min(1.0, float(item["score"])))
        if score <= 0:
            continue
        rows += (
            f'<tr><th scope="row">{esc(item["specialty"])}</th>'
            f'<td class="meter"><div class="bar"><i style="--v:{score:.3f}"></i></div></td>'
            f'<td class="num">{score:.2f}</td></tr>'
        )
    table = f'<table class="data"><tbody>{rows}</tbody></table>' if rows else ""
    body = f'<p class="finding">Suggested specialty</p><p class="verdict">{verdict}</p>{table}'
    return report("Routing report", body)


def scale_html(key: str) -> str:
    cells = "".join(
        f'<span class="{"on" if name.lower() == key else ""}">{name}</span>'
        for name in ["Low", "Medium", "High"]
    )
    return f'<div class="scale {key}">{cells}</div>'


def risk_slip(data: dict[str, Any]) -> str:
    key = risk_key(data["risk_level"])
    recommendation = (
        "Second opinion recommended"
        if data["second_opinion_recommended"]
        else "Second opinion not flagged"
    )
    body = (
        f'<p class="finding">Risk tier</p><p class="verdict {key}">{esc(data["risk_level"])}</p>'
        f"{scale_html(key)}<strong>{recommendation}</strong>"
    )
    return report("Risk assessment", body, data.get("explanation") or "")


def drug_slip(data: dict[str, Any]) -> str:
    key = risk_key(data["overall_risk"])
    rows = ""
    for pair in data["interactions"]:
        tier = risk_key(pair["risk_level"])
        rows += (
            f"<li><div><strong>{esc(pair['drug_a'])} + {esc(pair['drug_b'])}</strong>"
            f'<span class="tier {tier}">{esc(pair["risk_level"])}</span></div>'
            f"<p>{esc(pair.get('explanation') or 'No mechanism provided.')}</p></li>"
        )
    detail = (
        f'<ul class="pairs">{rows}</ul>' if rows else '<p class="empty">No interactions found.</p>'
    )
    body = (
        '<p class="finding">Overall risk</p>'
        f'<p class="verdict {key}">{esc(data["overall_risk"])}</p>{scale_html(key)}{detail}'
    )
    return report("Interaction report", body)


def validate_text(text: str) -> str | None:
    return None if text.strip() else "Enter some text first."


def validate_drugs(text: str) -> str | None:
    return None if len(parse_drugs(text)) >= 2 else "Enter at least two drugs."


TOOLS: dict[str, dict[str, Any]] = {
    "Symptom routing": {
        "id": "symptom",
        "title": "Symptom-to-specialty routing",
        "field": "Describe symptoms",
        "samples": SYMPTOM_SAMPLES,
        "button": "Route symptoms",
        "validate": validate_text,
        "run": predict_specialties,
        "slip": lambda text, data: specialty_slip(data),
    },
    "Second-opinion risk": {
        "id": "risk",
        "title": "Second-opinion risk assessment",
        "field": "Paste de-identified report",
        "samples": RISK_SAMPLES,
        "button": "Assess risk",
        "validate": validate_text,
        "run": assess_risk,
        "slip": lambda text, data: risk_slip(data),
    },
    "Drug interactions": {
        "id": "drug",
        "title": "Drug interaction screening",
        "field": "List drugs, one per line or comma-separated",
        "samples": DRUG_SAMPLES,
        "button": "Check interactions",
        "validate": validate_drugs,
        "run": lambda text: check_drugs(parse_drugs(text)),
        "slip": lambda text, data: drug_slip(data),
    },
}


def inject_css() -> None:
    css = (FRONTEND_DIR / "styles.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        f"""<div class="hero"><h1>Healthcare Intelligence Engine</h1>
<a href="{REPO_URL}" target="_blank" rel="noopener">View source</a></div>
<div class="notice" role="note"><strong>Demonstration only.</strong> Synthetic data. Not medical advice.</div>""",
        unsafe_allow_html=True,
    )


def load_sample(tool_id: str, samples: dict[str, str]) -> None:
    choice = st.session_state.get(f"{tool_id}_sample")
    if choice:
        st.session_state[f"{tool_id}_text"] = samples[choice]


def render_tool(tool: dict[str, Any]) -> None:
    tool_id, samples = tool["id"], tool["samples"]
    text_key, result_key = f"{tool_id}_text", f"{tool_id}_result"
    st.session_state.setdefault(text_key, next(iter(samples.values())))

    left, right = st.columns([5, 6], gap="large")
    error = None
    with left:
        st.markdown(
            f'<div class="tool-intro"><h2>{esc(tool["title"])}</h2></div>',
            unsafe_allow_html=True,
        )
        st.pills(
            "Load a sample",
            list(samples),
            key=f"{tool_id}_sample",
            on_change=load_sample,
            args=(tool_id, samples),
        )
        text = st.text_area(tool["field"], key=text_key, height=150)
        if st.button(tool["button"], key=f"{tool_id}_run", type="primary"):
            st.session_state.pop(result_key, None)
            error = tool["validate"](text)
            if error is None:
                try:
                    st.session_state[result_key] = {"input": text, "data": tool["run"](text)}
                except Exception as exc:
                    error = f"Unable to complete the demo request: {exc}"
        if error:
            st.error(error)

    result = st.session_state.get(result_key)
    is_current = result is not None and result["input"] == text
    with right:
        if is_current:
            st.html(tool["slip"](text, result["data"]))
        else:
            message = (
                "The input changed. Run the check again to refresh this report."
                if result
                else "No report yet. Submit the form to generate one."
            )
            st.html(report("Report", f'<p class="empty">{message}</p>'))


st.set_page_config(page_title="Healthcare Intelligence Engine", layout="wide")
inject_css()
render_header()
selected = st.radio("Tool", list(TOOLS), horizontal=True, key="tool", label_visibility="collapsed")
render_tool(TOOLS[selected])
