# libs

Shared Python modules used by the **FastAPI service** and **Ray ingestion** so embeddings and types stay consistent end to end.

## Embeddings (`embeddings/`)

`cpu.py` loads **SentenceTransformer** `BAAI/bge-small-en-v1.5` on **CPU** (`CUDA_VISIBLE_DEVICES` cleared) and exposes `embed_texts()` for batch encoding. The ingestion pipeline’s `BatchEmbedder` and the API’s embedding client both rely on this path so **query vectors and index vectors live in the same space**—critical for Qdrant similarity search to behave correctly.

## Observability (`observability/`)

`tracing.py` provides lightweight tracing/logging helpers without requiring a full OpenTelemetry stack on constrained environments.

## Schemas (`schemas/chat.py`)

Pydantic models (`ChatRequest`, `ChatResponse`, `Message`, `RetrievalResult`, etc.) define stable shapes for HTTP APIs and internal agent nodes.

## Retry (`retry/backoff.py`)

Backoff helpers for resilient calls to external services.

## Utils (`utils/`)

`ids.py` — identifier helpers.  
`timing.py` — timing utilities for latency-sensitive paths.

## Import paths

Imports assume `rag-core` is on `PYTHONPATH` (or an equivalent package layout in Docker/Kubernetes/Ray).
