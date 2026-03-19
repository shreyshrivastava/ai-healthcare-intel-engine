import os

import requests
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Healthcare Intelligence Engine", layout="wide")

st.title("AI Healthcare Intelligence Engine")
st.caption("Symptom-to-specialist matching, second-opinion risk, and drug interaction checks.")


tab1, tab2, tab3 = st.tabs(
    ["🧑‍⚕️ Symptom → Specialist", "📝 Second Opinion Risk", "💊 Drug Interactions"]
)


with tab1:
    st.subheader("Symptom to Specialist Matching")
    symptoms_text = st.text_area("Describe the patient's symptoms", height=160)
    if st.button("Predict Specialist", key="predict_specialist"):
        if not symptoms_text.strip():
            st.warning("Please enter symptoms text.")
        else:
            resp = requests.post(
                f"{API_URL}/symptom-specialist/predict",
                json={"symptoms_text": symptoms_text},
                timeout=300,
            )
            if resp.ok:
                data = resp.json()
                st.write("### Ranked Specialties")
                for item in data["ranked_specialties"]:
                    st.write(f"- **{item['specialty']}** — score: `{item['score']:.2f}`")
                if data.get("explanation"):
                    st.info(data["explanation"])
            else:
                st.error(f"API error: {resp.status_code} {resp.text}")


with tab2:
    st.subheader("Second Opinion Risk Stratifier")
    report_text = st.text_area("Paste diagnosis summary or report", height=200)
    if st.button("Assess Risk", key="assess_risk"):
        if not report_text.strip():
            st.warning("Please paste a report.")
        else:
            resp = requests.post(
                f"{API_URL}/second-opinion/assess",
                json={"report_text": report_text},
                timeout=300,
            )
            if resp.ok:
                data = resp.json()
                st.write(f"### Risk Level: **{data['risk_level']}**")
                st.write(
                    f"Second opinion recommended: "
                    f"**{'Yes' if data['second_opinion_recommended'] else 'No'}**"
                )
                if data.get("explanation"):
                    st.info(data["explanation"])
            else:
                st.error(f"API error: {resp.status_code} {resp.text}")


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
        else:
            resp = requests.post(
                f"{API_URL}/drug-interactions/check",
                json={"drugs": drugs},
                timeout=300,
            )
            if resp.ok:
                data = resp.json()
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
                    st.success("No interactions detected by the current stub logic.")
            else:
                st.error(f"API error: {resp.status_code} {resp.text}")

