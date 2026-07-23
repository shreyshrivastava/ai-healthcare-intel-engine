from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from core.models import get_symptom_encoder
from core.vector_store import InMemoryVectorStore, VectorStoreItem

DEMO_DATA_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "demo" / "symptom_specialist_cases.json"
)


@dataclass
class RankedSpecialtyResult:
    specialty: str
    score: float


def display_specialty(raw_specialty: str) -> str:
    cleaned = raw_specialty.strip()
    if "/" in cleaned:
        return "/".join(part.strip().title() for part in cleaned.split("/"))
    return cleaned.title()


class SymptomSpecialistEngine:
    """
    Embedding-based symptom-to-specialist matcher backed by a small demo corpus.
    In a real setup this would index many thousands of historical cases.
    """

    def __init__(self) -> None:
        self.encoder = get_symptom_encoder()
        self._vector_store = self._build_store_from_demo()

    def _build_store_from_demo(self) -> InMemoryVectorStore:
        if not DEMO_DATA_PATH.exists():
            return InMemoryVectorStore([])

        with DEMO_DATA_PATH.open("r", encoding="utf-8") as f:
            raw_cases: list[dict[str, str]] = json.load(f)

        texts = [c["text"] for c in raw_cases]
        specialties = [display_specialty(c["specialty"]) for c in raw_cases]

        embeddings = self.encoder.encode(texts, convert_to_numpy=True)
        items = [
            VectorStoreItem(vector=embeddings[i], label=specialties[i]) for i in range(len(texts))
        ]
        return InMemoryVectorStore(items)

    def rank_specialties(
        self,
        symptoms_text: str,
        top_k: int = 5,
    ) -> tuple[list[RankedSpecialtyResult], str]:
        if not symptoms_text.strip():
            return [], "No symptoms provided."

        query_vec = self.encoder.encode([symptoms_text], convert_to_numpy=True)[0]
        neighbors = self._vector_store.search(query_vec, top_k=top_k)

        if not neighbors:
            return [], "No similar cases available in the demo corpus."

        scores_by_specialty: dict[str, list[float]] = {}
        for specialty, score in neighbors:
            scores_by_specialty.setdefault(specialty, []).append(score)

        aggregated: list[RankedSpecialtyResult] = []
        for specialty, scores in scores_by_specialty.items():
            aggregated.append(
                RankedSpecialtyResult(specialty=specialty, score=float(np.mean(scores)))
            )

        aggregated.sort(key=lambda x: x.score, reverse=True)

        explanation = (
            "Specialties ranked using embedding similarity against a small set of demo cases. "
            "In a production setup this would use a much larger, clinically curated corpus."
        )
        return aggregated[:top_k], explanation


_engine: SymptomSpecialistEngine | None = None


def get_engine() -> SymptomSpecialistEngine:
    global _engine
    if _engine is None:
        _engine = SymptomSpecialistEngine()
    return _engine
