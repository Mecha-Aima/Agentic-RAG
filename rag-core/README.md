# rag-core

Core code for the RAG platform: **API**, **ingestion pipelines**, **shared libraries**, **deployment manifests**, and **AWS infrastructure** (Terraform).

## How RAG works here

Retrieval is split across **two stores** that are filled by the same ingestion run and queried at answer time:

1. **Vector store (Qdrant)** — Chunk-level **dense embeddings** (CPU `BAAI/bge-small-en-v1.5` via `libs.embeddings.cpu`). Used for *semantic similarity*: “which passages are closest to this question?”
2. **Graph store (Neo4j)** — **Structured entities and relationships** extracted from chunks by an LLM (`GraphExtractor` uses Groq with a fixed JSON schema). Used for *relational context*: “who is connected to what?”

At **query time**, the FastAPI service connects to both systems (plus Postgres for sessions/metadata, Redis for caching, and Groq for the agent/LLM). Agent tools embed the user question and search Qdrant, or derive entity names and run **parameterized Cypher** against Neo4j—so the two backends complement each other rather than duplicate work.

**Ingestion** (Ray pipeline under `pipelines/ingestion/`) reads raw files from S3, chunks and enriches text, runs embedding and graph extraction in parallel branches, then **upserts** vectors into Qdrant and **MERGE**s nodes/edges into Neo4j. See `pipelines/README.md` for the full pipeline and environment variables.

## Layout

| Path | Role |
|------|------|
| `services/api/` | FastAPI application: chat, upload, health; agent graph; vector/graph tools; Redis, Neo4j, Qdrant, embedding and LLM clients |
| `services/sandbox/` | Isolated Flask service that executes Python code in a subprocess with timeouts (for agent tooling) |
| `services/gateway/` | Redis Lua script for rate limiting |
| `pipelines/` | Ray-based document ingestion and Lambda-triggered ingestion jobs |
| `libs/` | Shared Python helpers (embeddings, schemas, retry, observability, utils) |
| `deploy/` | Kubernetes manifests for running API, Qdrant, Redis, and sandbox in-cluster |
| `infra/terraform/` | AWS resources: VPC, EC2, RDS, S3, ECR, Lambda (S3 → Ray job), IAM, budgets |

## Configuration surfaces

- **API** — Environment-driven settings in `services/api/app/config.py` (`DATABASE_URL`, `REDIS_URL`, `QDRANT_*`, `NEO4J_*`, `S3_BUCKET_NAME`, `GROQ_API_KEY`, JWT, etc.).
- **Ingestion workers** — Ray tasks and indexers read **`QDRANT_HOST` / `QDRANT_PORT` / `QDRANT_COLLECTION`**, **`NEO4J_URI` / `NEO4J_USER` / `NEO4J_PASSWORD`**, and **`GROQ_API_KEY`** (for graph extraction). Align collection names and credentials with whatever the API uses so search hits the same data.

## Local dependencies

The repo root `docker-compose.yml` provides Postgres, Redis, Qdrant, and Neo4j for local development.

## Related docs

- `pipelines/README.md` — ingestion stages, extraction, and indexers  
- `libs/README.md` — shared packages  
- `deploy/README.md` — Kubernetes deployment and service wiring  
- `infra/README.md` — Terraform and cloud setup  
