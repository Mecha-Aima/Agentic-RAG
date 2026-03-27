from typing import Any, Dict

from libs.embeddings.cpu import embed_texts


class BatchEmbedder:
    """
    Ray Data callable: CPU embeddings via shared bge-small model.
    """

    def __call__(self, batch: Dict[str, Any]) -> Dict[str, Any]:
        texts = batch["text"]
        try:
            embeddings = embed_texts(texts)
            batch["vector"] = embeddings
            return batch
        except Exception as e:
            raise e
