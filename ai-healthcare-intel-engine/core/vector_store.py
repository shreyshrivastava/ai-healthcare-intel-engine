from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np


@dataclass
class VectorStoreItem:
    vector: np.ndarray
    label: str


class InMemoryVectorStore:
    """
    Lightweight cosine-similarity store for deterministic demos and tests.

    A production version can swap this for FAISS or a managed vector database,
    but the portfolio demo should not require native FAISS wheels in CI.
    """

    def __init__(self, items: Sequence[VectorStoreItem]) -> None:
        self._labels: list[str] = []
        if not items:
            self._vectors = np.zeros((0, 0), dtype=np.float32)
        else:
            vectors = np.stack([it.vector for it in items]).astype(np.float32)
            self._vectors = _normalize_rows(vectors)
            self._labels = [it.label for it in items]

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> list[tuple[str, float]]:
        if self._vectors.size == 0 or top_k <= 0:
            return []

        query = _normalize_rows(query_vector.astype(np.float32).reshape(1, -1))[0]
        if not np.any(query):
            return []

        scores = self._vectors @ query
        top_indices = np.argsort(scores)[::-1][: min(top_k, len(self._labels))]
        return [(self._labels[idx], float(scores[idx])) for idx in top_indices]


def _normalize_rows(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return np.divide(vectors, norms, out=np.zeros_like(vectors), where=norms > 0)
