from __future__ import annotations

import re
from dataclasses import dataclass

HIGH_RISK_KEYWORDS = [
    "acute pulmonary embolism",
    "altered mental status",
    "hemoglobin dropped",
    "high-flow nasal cannula",
    "intubated",
    "metastatic",
    "myocardial infarction",
    "metastatic",
    "multi organ failure",
    "neutropenic fever",
    "sepsis",
    "septic shock",
    "status epilepticus",
    "stroke",
    "subarachnoid hemorrhage",
    "intensive care",
    "ventilator",
    "vasopressors",
    "icu",
]

MEDIUM_RISK_KEYWORDS = [
    "acute appendicitis",
    "acute kidney injury",
    "atrial fibrillation",
    "cirrhosis",
    "complicated",
    "creatinine",
    "microalbuminuria",
    "moderate ascites",
    "multiple comorbidities",
    "poorly controlled",
    "recurrent",
    "surgery planned",
]


@dataclass
class SecondOpinionPrediction:
    risk_level: str
    second_opinion_recommended: bool
    contributing_phrases: list[str]


def assess_report_text(report_text: str) -> SecondOpinionPrediction:
    text = _normalize_text(report_text)
    hits_high = [keyword for keyword in HIGH_RISK_KEYWORDS if _phrase_present(text, keyword)]
    hits_medium = [keyword for keyword in MEDIUM_RISK_KEYWORDS if _phrase_present(text, keyword)]

    if hits_high:
        return SecondOpinionPrediction(
            risk_level="High",
            second_opinion_recommended=True,
            contributing_phrases=hits_high,
        )
    if hits_medium:
        return SecondOpinionPrediction(
            risk_level="Medium",
            second_opinion_recommended=True,
            contributing_phrases=hits_medium,
        )

    return SecondOpinionPrediction(
        risk_level="Low",
        second_opinion_recommended=False,
        contributing_phrases=[],
    )


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _phrase_present(text: str, phrase: str) -> bool:
    pattern = rf"(?<![a-z0-9]){re.escape(phrase)}(?![a-z0-9])"
    for match in re.finditer(pattern, text):
        prefix = text[max(0, match.start() - 24) : match.start()]
        if re.search(r"\b(no|without|denies|negative for)\s+$", prefix):
            continue
        return True
    return False
