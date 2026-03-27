# deploy

Kubernetes manifests for running the RAG stack on a cluster (e.g. K3s on the Terraform-provisioned host).

## How the pieces connect

In a typical deployment, the **API** pod must reach **Qdrant**, **Neo4j**, **Redis**, and **Postgres** (often RDS outside the cluster) using the same logical names and credentials you use for **ingestion**. Configure these via the `rag-secrets` Secret (or equivalent) so they match `services/api/app/config.py`:

- **`QDRANT_HOST` / `QDRANT_PORT` / `QDRANT_COLLECTION`** — The API’s `VectorDBClient` performs async similarity search over the collection that **ingestion** populated; service DNS inside the cluster (e.g. a `qdrant` Service) should match the host you set here.
- **`NEO4J_URI` / `NEO4J_USER` / `NEO4J_PASSWORD`** — The API’s `Neo4jClient` runs async Cypher for graph-backed tools; the Bolt URL may point to an in-cluster Neo4j, **Neo4j Aura**, or a host reachable from the cluster.
- **`REDIS_URL`** — Session/cache layer for the API (co-locate with the API or use a managed Redis if you move off in-cluster Redis).
- **`DATABASE_URL`** — Postgres for application state (often the Terraform RDS endpoint).

**Qdrant** and **Redis** manifests in this folder give you in-cluster options; Neo4j may be external (Aura) depending on your Terraform and ops model. The **sandbox** Deployment is separate: it runs untrusted code for agent tools and should stay **network-isolated** (see `sandbox-network-policy.yaml`) while still callable from the API according to your security design.

## Kubernetes (`k8s/`)

| Manifest | Purpose |
|----------|---------|
| `api-deployment.yaml` | `rag-api` Deployment and Service (port 8000); probes on `/health/liveness`; env from `rag-secrets` |
| `qdrant-deployment.yaml` | Qdrant vector store for dense retrieval |
| `redis-deployment.yaml` | Redis for API caching / sessions |
| `sandbox-deployment.yaml` | Code-execution sandbox service |
| `sandbox-network-policy.yaml` | Network policy for sandbox isolation |

## Image and secrets

- Replace `PLACEHOLDER_ECR_API_REPOSITORY_URL` in the API manifest with the ECR URL from Terraform (see `infra` outputs).
- Create an ECR pull secret (e.g. `ecr-secret`) and reference it in `imagePullSecrets` as in the sample.
- Provide a `rag-secrets` Secret with application configuration: database URL, Redis URL, Qdrant and Neo4j endpoints, S3 bucket, Groq and JWT secrets, etc., aligned with ingestion workers so **vectors and graph data** written by pipelines are **read** by the same collection and database.

## SSH key

Terraform can output an SSH private key for the EC2 instance; save it securely and restrict file permissions (`chmod 600`). Do not commit private keys to version control.
