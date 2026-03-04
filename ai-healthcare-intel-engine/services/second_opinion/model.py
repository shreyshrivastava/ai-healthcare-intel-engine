from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


HIGH_RISK_KEYWORDS = [
    "metastatic",
    "septic shock",
    "sepsis",
    "multi organ failure",
    "intensive care",
    "icu",
    "ventilator",
    "stroke",
    "myocardial infarction",
]

MEDIUM_RISK_KEYWORDS = [
    "multiple comorbidities",
    "complicated",
    "poorly controlled",
    "recurrent",
    "surgery planned",
]


@dataclass
class SecondOpinionPrediction:
    risk_level: str
    second_opinion_recommended: bool
    contributing_phrases: List[str]


def assess_report_text(report_text: str) -> SecondOpinionPrediction:
    text = report_text.lower()
    hits_high = [k for k in HIGH_RISK_KEYWORDS if k in text]
    hits_medium = [k for k in MEDIUM_RISK_KEYWORDS if k in text]

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

