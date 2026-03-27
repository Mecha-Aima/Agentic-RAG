import logging
import os
from typing import Dict, List, Optional

import backoff
from groq import AsyncGroq

from services.api.app.config import settings

logger = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


class GroqLLMClient:
    """
    Async Groq client (replaces Ray Serve + vLLM on free tier).
    """

    def __init__(self) -> None:
        self._client: Optional[AsyncGroq] = None

    async def start(self) -> None:
        self._client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        logger.info("Groq LLM client initialized.")

    async def close(self) -> None:
        self._client = None

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def chat_completion(
        self,
        messages: List[Dict],
        temperature: float = 0.3,
        json_mode: bool = False,
    ) -> str:
        if not self._client:
            raise RuntimeError("Client not initialized. Call start() first.")

        kwargs = {
            "model": DEFAULT_MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 2048,
        }
        # Groq: prefer prompt-level JSON instructions; response_format varies by model.
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await self._client.chat.completions.create(**kwargs)
        except Exception:
            if json_mode and "response_format" in kwargs:
                kwargs.pop("response_format", None)
                response = await self._client.chat.completions.create(**kwargs)
            else:
                raise
        return response.choices[0].message.content or ""


# Backward-compatible alias for type hints / imports
RayLLMClient = GroqLLMClient
llm_client = GroqLLMClient()
