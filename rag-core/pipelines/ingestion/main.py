# pipelines/ingestion/main.py
import logging
import os
from typing import Any, Dict

import ray
from pipelines.ingestion.chunking.splitter import split_text
from pipelines.ingestion.embedding.compute import BatchEmbedder
from pipelines.ingestion.graph.extractor import GraphExtractor
from pipelines.ingestion.indexing.neo4j import Neo4jIndexer
from pipelines.ingestion.indexing.qdrant import QdrantIndexer
from pipelines.ingestion.loaders.pdf import parse_pdf_bytes

ray.init(address="auto")

logger = logging.getLogger(__name__)


def process_batch(batch: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ray Data transformation: parse files and chunk text.
    """
    results = []

    for i, content in enumerate(batch["bytes"]):
        path = batch.get("path", batch.get("filename", [""] * len(batch["bytes"])))[i]
        filename = os.path.basename(path) if path else f"object_{i}"
        raw_text, metadata = parse_pdf_bytes(content, filename)
        chunks = split_text(raw_text, chunk_size=512, overlap=50)
        for chunk in chunks:
            chunk["metadata"].update(metadata)
            results.append(chunk)

    return {"text": [r["text"] for r in results], "metadata": [r["metadata"] for r in results]}


def main(bucket_name: str, prefix: str) -> None:
    ds = ray.data.read_binary_files(
        paths=f"s3://{bucket_name}/{prefix}",
        include_paths=True,
    )

    chunked_ds = ds.map_batches(
        process_batch,
        batch_size=10,
        num_cpus=1,
    )

    vector_ds = chunked_ds.map_batches(
        BatchEmbedder,
        concurrency=1,
        num_gpus=0,
        batch_size=32,
    )

    graph_ds = chunked_ds.map_batches(
        GraphExtractor,
        concurrency=1,
        num_gpus=0,
        batch_size=2,
    )

    vector_ds.write_datasource(QdrantIndexer())
    graph_ds.write_datasource(Neo4jIndexer())

    print("Ingestion Job Completed Successfully.")


if __name__ == "__main__":
    import sys

    main(sys.argv[1], sys.argv[2])
