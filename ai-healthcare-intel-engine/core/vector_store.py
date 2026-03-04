from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

import numpy as np


@dataclass
class VectorStoreItem:
    vector: np.ndarray
    label: str


class InMemoryVectorStore:
    """
    Simple in-memory vector store using numpy and cosine similarity.
    This keeps the demo self-contained; you can later swap this out for FAISS.
    """

    def __init__(self, items: Sequence[VectorStoreItem]) -> None:
        if not items:
            self._vectors = np.zeros((0, 1), dtype=np.float32)
            self._labels: List[str] = []
        else:
            self._vectors = np.stack([it.vector for it in items]).astype(np.float32)
            self._labels = [it.label for it in items]

        norms = np.linalg.norm(self._vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self._vectors = self._vectors / norms

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        if self._vectors.shape[0] == 0:
            return []

        q = query_vector.astype(np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm == 0:
            return []
        q = q / q_norm

        scores = self._vectors @ q
        idx = np.argsort(scores)[::-1][:top_k]
        return [(self._labels[i], float(scores[i])) for i in idx]

