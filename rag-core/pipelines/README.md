# pipelines

Document **ingestion** (Ray) and **event-driven jobs** (Lambda → Ray) that populate the vector and graph databases used by the RAG API.

---

## Ingestion overview (`ingestion/`)

Ingestion turns raw files in S3 into **searchable chunks in Qdrant** and **entities/relationships in Neo4j**. The orchestrator is `main.py`: it uses **Ray Data** to scale I/O and CPU work, branches into two logical paths from the same chunked text, and writes to both backends.

### End-to-end flow

1. **Read from object storage** — `ray.data.read_binary_files` loads files from `s3://<bucket>/<prefix>` with paths preserved for provenance.
2. **Parse and chunk** — `process_batch` (in `main.py`) uses loaders such as `loaders/pdf.py` to extract text and metadata (e.g. filename, page), then `chunking/splitter.py` splits text into overlapping segments (defaults are wired in code; `config.yaml` also describes chunking and collection settings for operators).
3. **Branch A — Embeddings (vector index)** — `embedding/compute.py` defines `BatchEmbedder`, which calls `libs.embeddings.cpu.embed_texts` (**SentenceTransformer** `BAAI/bge-small-en-v1.5` on CPU). Each chunk gets a dense vector used only for semantic retrieval.
4. **Branch B — Graph extraction** — `graph/extractor.py` defines `GraphExtractor`, which calls **Groq** with a prompt built from `graph/schema.py`. The model returns **JSON** with `nodes` (`id`, `type`) and `edges` (`source`, `target`, `type`) constrained to a fixed vocabulary of labels and relation types, so the graph stays consistent across documents.
5. **Write vectors** — `indexing/qdrant.py` (`QdrantIndexer`) uses the synchronous `qdrant_client` to **upsert** points: each point has a UUID, the embedding vector, and a **payload** with chunk text and source metadata (e.g. filename, page) for citation-style retrieval.
6. **Write graph** — `indexing/neo4j.py` (`Neo4jIndexer`) uses the Neo4j Python driver to run a **batch transaction**: it flattens `graph_nodes` / `graph_edges` from the Ray batch, then **MERGE**s `(:Entity {name})` nodes and **`RELATED`** relationships in Cypher so repeated runs are idempotent.

The embedding path and graph path both start from the **same chunked dataset**; they are separate `map_batches` / `write_datasource` chains, so vector and graph indexing can be tuned independently (concurrency, batch sizes).

### Configuration (`config.yaml`)

YAML covers **chunking** (size, overlap, separators), **embedding** batch sizing, **graph** concurrency and schema enforcement flags, and **vector_db** (collection name and distance metric). Runtime overrides for hosts and credentials come from **environment variables** (see below).

### Environment variables (ingestion / Ray workers)

| Area | Variables | Role |
|------|-----------|------|
| **Qdrant** | `QDRANT_HOST`, `QDRANT_PORT`, `QDRANT_COLLECTION` | Target cluster and collection; must match what the API uses (`services/api/app/config.py`). |
| **Neo4j** | `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | Bolt URL and credentials for graph writes. |
| **Graph LLM** | `GROQ_API_KEY`, optional `GROQ_MODEL` | Required for `GraphExtractor`; model defaults to `llama-3.3-70b-versatile` if unset. |

Ray is initialized with `ray.init(address="auto")` so workers can join an existing cluster (typical on the EC2 ingest host).

### Entrypoint

```text
python -m pipelines.ingestion.main <bucket> <prefix>
```

Arguments are the S3 bucket and key prefix to scan for files to process.

---

## Jobs (`jobs/`)

### `s3_event_handler.py`

**Lambda** entry point for S3 `ObjectCreated` notifications. For each record it derives the bucket and key, then submits work to the **Ray Job Submission HTTP API** (`RAY_ADDRESS`, default `http://127.0.0.1:8265`) so the heavy ingestion code runs on the Ray cluster, not inside Lambda.

Requirements on the ingest host:

- `rag-core` available at `RAG_CODE_ROOT` (default `/opt/rag-core`) on `PYTHONPATH`
- A `.env` (or equivalent) with database URLs, Qdrant/Neo4j settings, `GROQ_API_KEY`, and AWS credentials as needed for S3/Ray

Use this when new uploads to the documents bucket should **trigger ingestion automatically** in AWS.
