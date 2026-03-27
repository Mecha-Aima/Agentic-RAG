# services/api/app/models/vllm_engine.py
# Legacy name kept for imports; implementation is Groq (no GPU / vLLM on free tier).
import os
from typing import Any, Dict, List

from groq import AsyncGroq

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


async def generate(
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> Dict[str, Any]:
    """Groq chat completion shaped like a minimal OpenAI-compatible response."""
    client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])
    response = await client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    content = response.choices[0].message.content
    return {
        "choices": [
            {"message": {"content": content, "role": "assistant"}}
        ]
    }
