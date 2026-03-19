from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple

import numpy as np
import faiss

@dataclass
class VectorStoreItem:
    vector: np.ndarray
    label: str

class InMemoryVectorStore:
    """
    Enterprise Vector Store using FAISS (Facebook AI Similarity Search).
    Provides scalable similarity search over embeddings instead of naive numpy arrays.
    """

    def __init__(self, items: Sequence[VectorStoreItem]) -> None:
        self._labels: List[str] = []
        if not items:
            self._vectors = np.zeros((0, 1), dtype=np.float32)
            self.index = None
        else:
            self._dim = items[0].vector.shape[0]
            # Use Inner Product (IP), which implies Cosine Similarity if L2 normalized
            self.index = faiss.IndexFlatIP(self._dim)
            
            vectors = np.stack([it.vector for it in items]).astype(np.float32)
            # Normalize vectors to use Inner Product equivalently to Cosine Similarity
            faiss.normalize_L2(vectors)
            
            self.index.add(vectors)
            self._labels = [it.label for it in items]

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        if self.index is None or self.index.ntotal == 0:
            return []

        q = query_vector.astype(np.float32).reshape(1, -1)
        faiss.normalize_L2(q)

        scores, indices = self.index.search(q, top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0: # Ensure valid index
                results.append((self._labels[idx], float(score)))
                
        return results
