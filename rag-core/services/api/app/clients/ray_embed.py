import asyncio
import logging
from typing import List

from libs.embeddings.cpu import embed_texts

logger = logging.getLogger(__name__)


class CPUEmbedClient:
    """
    In-process CPU embeddings (replaces Ray Serve embed service).
    """

    async def start(self) -> None:
        # Warm model once on startup (loads SentenceTransformer)
        await asyncio.to_thread(embed_texts, ["warmup"])
        logger.info("CPU embed client initialized.")

    async def close(self) -> None:
        pass

    async def embed_query(self, text: str) -> List[float]:
        vectors = await asyncio.to_thread(embed_texts, [text])
        return vectors[0]

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return await asyncio.to_thread(embed_texts, texts)


RayEmbedClient = CPUEmbedClient
embed_client = CPUEmbedClient()
