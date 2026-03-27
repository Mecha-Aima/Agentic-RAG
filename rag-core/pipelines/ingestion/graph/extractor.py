# pipelines/ingestion/graph/extractor.py
import json
import os
from typing import Any, Dict, List

from groq import Groq

from pipelines.ingestion.graph.schema import GraphSchema

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


class GraphExtractor:
    """
    Ray Data callable: graph extraction via Groq (CPU/free tier — no Ray LLM service).
    """

    def __init__(self) -> None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is required for graph extraction")
        self._client = Groq(api_key=api_key)

    def __call__(self, batch: Dict[str, Any]) -> Dict[str, Any]:
        nodes_list: List = []
        edges_list: List = []

        for text in batch["text"]:
            try:
                prompt = f"""
                {GraphSchema.get_system_prompt()}

                Input Text:
                {text}
                """
                response = self._client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=1024,
                )
                content = response.choices[0].message.content or ""
                graph_data = json.loads(content)
                nodes_list.append(graph_data.get("nodes", []))
                edges_list.append(graph_data.get("edges", []))
            except Exception as e:
                print(f"Graph extraction failed for chunk: {e}")
                nodes_list.append([])
                edges_list.append([])

        batch["graph_nodes"] = nodes_list
        batch["graph_edges"] = edges_list
        return batch
