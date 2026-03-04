from functools import lru_cache

from sentence_transformers import SentenceTransformer


SYMPTOM_ENCODER_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_symptom_encoder() -> SentenceTransformer:
    """
    Shared sentence-level encoder for symptom text.
    Cached so it is loaded only once per process.
    """
    return SentenceTransformer(SYMPTOM_ENCODER_MODEL_NAME)

