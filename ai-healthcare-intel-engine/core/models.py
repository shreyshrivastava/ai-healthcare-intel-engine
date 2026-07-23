from __future__ import annotations

import logging
import os
import re
from collections.abc import Sequence
from functools import lru_cache
from typing import Protocol

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_SYMPTOM_ENCODER_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_EMBEDDING_BACKEND = "keyword"

CLINICAL_KEYWORDS = [
    "abdominal pain",
    "back pain",
    "blood pressure",
    "blood sugar",
    "chest pain",
    "confusion",
    "cough",
    "delayed milestone",
    "diarrhea",
    "dizziness",
    "eye pain",
    "fatigue",
    "fever",
    "flank pain",
    "hearing loss",
    "heart palpitations",
    "hot flashes",
    "infections",
    "insomnia",
    "irregular borders",
    "joint pain",
    "lymph nodes",
    "memory loss",
    "menstrual",
    "nausea",
    "night sweats",
    "numbness",
    "pelvic pain",
    "rash",
    "shortness of breath",
    "sinus pressure",
    "skin lesion",
    "sore throat",
    "swelling",
    "urination",
    "vision",
    "vomiting",
    "weight loss",
    "wheezing",
]


class SymptomEncoder(Protocol):
    def encode(self, texts: Sequence[str], convert_to_numpy: bool = True):
        """Return one vector per input text."""


class KeywordSymptomEncoder:
    """
    Deterministic encoder used by CI, tests, and public cloud demos.

    It avoids model downloads while preserving a meaningful similarity signal for
    the synthetic demo corpus. Local users can opt into sentence-transformers by
    setting HEALTHCARE_EMBEDDING_BACKEND=sentence-transformer.
    """

    def __init__(self, keywords: Sequence[str] | None = None) -> None:
        self.keywords = tuple(keywords or CLINICAL_KEYWORDS)

    def encode(self, texts: Sequence[str], convert_to_numpy: bool = True):
        vectors = np.vstack([self._encode_one(text) for text in texts]).astype(np.float32)
        return vectors if convert_to_numpy else vectors.tolist()

    def _encode_one(self, text: str) -> np.ndarray:
        normalized = re.sub(r"\s+", " ", text.lower())
        tokens = re.findall(r"[a-z][a-z-]+", normalized)
        token_set = set(tokens)
        vector = np.zeros(len(self.keywords), dtype=np.float32)

        for idx, keyword in enumerate(self.keywords):
            if " " in keyword:
                vector[idx] = float(normalized.count(keyword))
            elif keyword in token_set:
                vector[idx] = 1.0

        return vector


def _embedding_backend() -> str:
    return os.getenv("HEALTHCARE_EMBEDDING_BACKEND", DEFAULT_EMBEDDING_BACKEND).strip().lower()


def _model_name() -> str:
    return os.getenv("SYMPTOM_ENCODER_MODEL_NAME", DEFAULT_SYMPTOM_ENCODER_MODEL_NAME).strip()


@lru_cache(maxsize=1)
def get_symptom_encoder() -> SymptomEncoder:
    backend = _embedding_backend()
    if backend in {"sentence-transformer", "sentence_transformer", "transformer", "ml"}:
        try:
            from sentence_transformers import SentenceTransformer

            model_name = _model_name()
            logger.info("Loading sentence-transformer symptom encoder: %s", model_name)
            return SentenceTransformer(model_name)
        except Exception as exc:
            logger.warning("Falling back to keyword symptom encoder: %s", exc)

    return KeywordSymptomEncoder()
