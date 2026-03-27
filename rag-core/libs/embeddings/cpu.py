"""
CPU embeddings (BAAI/bge-small-en-v1.5) shared by FastAPI and Ray ingestion.
"""
from __future__ import annotations

import os

# Force CPU before importing torch-backed libs
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

from typing import List

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cpu")
    return _model


def embed_texts(texts: List[str], normalize: bool = True) -> List[List[float]]:
    """Encode a batch of strings to vectors (list of floats per text)."""
    if isinstance(texts, str):
        texts = [texts]
    if not texts:
        return []
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=normalize)
    return vectors.tolist()
