from __future__ import annotations

from typing import List

from api.schemas import RankedSpecialty
from .model import get_engine


def predict_ranked_specialties(symptoms_text: str) -> List[RankedSpecialty]:
    engine = get_engine()
    ranked, _ = engine.rank_specialties(symptoms_text)
    return [RankedSpecialty(specialty=r.specialty, score=r.score) for r in ranked]

