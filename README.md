# Agentic-RAG

Production-oriented **Agentic Retrieval-Augmented Generation (RAG)** platform that combines:

- **Vector retrieval** (Qdrant + dense embeddings)
- **Graph retrieval** (Neo4j knowledge graph)
- **Agent orchestration** (LangGraph workflow)
- **Streaming chat API** (FastAPI)
- **Event-driven ingestion** (S3 → Lambda → Ray jobs)

The repository is organized around `rag-core/` (application code), with root-level tooling for local development (`docker-compose.yml`, `.env.example`).

---

## What this project does

This system ingests documents from object storage, transforms them into:

1. **Semantic chunks and embeddings** for similarity search in Qdrant
2. **Entities and relationships** for graph exploration in Neo4j

At query time, the API agent can combine vector context, graph context, and optional tools (web search, calculator, sandboxed Python execution) to produce grounded answers.

---

## Architecture at a glance

### Ingestion path

`S3 documents` → `Ray ingestion pipeline` → `Chunking/metadata` →  
`Embedding branch` → `Qdrant upsert`  
`Graph extraction branch` → `Neo4j MERGE`

### Query path

`Client` → `FastAPI /api/v1/chat/stream` → `LangGraph nodes (planner/tool/retriever/responder)` →  
`Qdrant + Neo4j (+ optional tools)` → `streamed NDJSON answer`

---

## Repository structure

```text
.
├── docker-compose.yml          # Local Postgres, Redis, Qdrant, Neo4j
├── .env.example                # Example environment configuration
├── scripts/                    # Utilities (S3 bulk upload, docs scraping)
└── rag-core/
    ├── services/
    │   ├── api/                # FastAPI app, agent graph, tools, clients
    │   ├── sandbox/            # Isolated Python execution service
    │   └── gateway/            # Redis Lua rate limit script
    ├── pipelines/              # Ray ingestion + Lambda job handlers
    ├── libs/                   # Shared embeddings/schemas/retry/utils
    ├── deploy/                 # Kubernetes manifests
    └── infra/terraform/        # AWS infrastructure as code
```

---

## Core components

- **API service** (`rag-core/services/api`)
  - Streaming chat endpoint
  - JWT-protected routes
  - Semantic cache (Redis)
  - Conversation memory (Postgres)
  - Agent tool calling (vector search, graph search, web, calculator, sandbox)

- **Ingestion pipeline** (`rag-core/pipelines/ingestion`)
  - Reads files from S3
  - Parses/chunks documents
  - Generates embeddings with `BAAI/bge-small-en-v1.5`
  - Extracts graph entities/edges using Groq JSON output
  - Writes to Qdrant and Neo4j

- **Sandbox service** (`rag-core/services/sandbox`)
  - Executes Python in a separate process with timeout controls
  - Intended to run in an isolated network boundary

---

## Local development quickstart

### 1) Start infrastructure dependencies

From repository root:

```bash
docker compose up -d
```

Starts local:
- Postgres (`localhost:5432`)
- Redis (`localhost:6379`)
- Qdrant (`localhost:6333`)
- Neo4j (`localhost:7474`, Bolt `localhost:7687`)

### 2) Configure environment

```bash
cp .env.example .env
```

Set required values in `.env` (at minimum: database, Neo4j password, S3 bucket, Groq API key, JWT secret).

### 3) Install API dependencies

```bash
cd rag-core/services/api
pip install -r requirements.txt
```

### 4) Run API

From `rag-core/`:

```bash
uvicorn services.api.main:app --reload --host 0.0.0.0 --port 8000 --env-file ../.env
```

Health endpoints:
- `GET /health/liveness`
- `GET /health/readiness`

---

## Key environment variables

| Area | Variables |
|------|-----------|
| App/runtime | `ENV`, `LOG_LEVEL` |
| Auth | `JWT_SECRET_KEY`, `JWT_ALGORITHM` |
| Postgres | `DATABASE_URL` |
| Redis | `REDIS_URL` |
| Qdrant | `QDRANT_HOST`, `QDRANT_PORT`, `QDRANT_COLLECTION` |
| Neo4j | `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` |
| AWS/S3 | `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME` |
| LLM/tooling | `GROQ_API_KEY`, `TAVILY_API_KEY` |

> Keep API and ingestion configuration aligned (especially Qdrant collection and Neo4j credentials), or retrieval will not see newly ingested data.

---

## Running ingestion

From `rag-core/`:

```bash
python -m pipelines.ingestion.main <bucket> <prefix>
```

This scans `s3://<bucket>/<prefix>`, processes files, and updates both Qdrant and Neo4j.

For event-driven ingestion in AWS, use `pipelines/jobs/s3_event_handler.py` with S3 notifications and Ray Job Submission API.

---

## Deployment options

- **Kubernetes manifests**: `rag-core/deploy/k8s/`
- **Terraform (AWS)**: `rag-core/infra/terraform/`

Typical production shape:
- API + optional in-cluster Redis/Qdrant on Kubernetes
- Managed/external Postgres and/or Neo4j
- S3 for document storage
- Lambda trigger to submit ingestion jobs to Ray

---

## Security notes

- Do not commit secrets; use environment variables and Kubernetes Secrets.
- Keep sandbox service isolated (network policy + strict exposure).
- JWT is required for protected API routes.
- Graph retrieval uses parameterized Cypher patterns to reduce injection risk.

---

## Additional documentation

- `rag-core/README.md` — core architecture summary
- `rag-core/pipelines/README.md` — ingestion and jobs
- `rag-core/deploy/README.md` — Kubernetes deployment wiring
- `rag-core/infra/README.md` — Terraform infrastructure details
- `rag-core/libs/README.md` — shared library modules
- `scripts/README.md` — utility scripts
