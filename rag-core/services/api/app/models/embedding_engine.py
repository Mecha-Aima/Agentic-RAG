# CPU embeddings (no Ray Serve / GPU on free tier)
from __future__ import annotations

from typing import List, Sequence, Union

from libs.embeddings.cpu import embed_texts


def embed(texts: Union[str, Sequence[str]]) -> List[List[float]]:
    if isinstance(texts, str):
        return embed_texts([texts])
    return embed_texts(list(texts))
