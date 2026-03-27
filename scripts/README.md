# scripts

Utility scripts for data prep and AWS uploads.

## `bulk_upload_s3.py`

Uploads a local directory to an S3 bucket using multipart transfer. Uses `boto3`; can create the bucket if missing (when permissions allow). Set `AWS_REGION` as needed.

**Typical use:** sync local documents into the ingestion bucket before or alongside pipeline runs.

## `scrape_kubernetes_docs.py`

Fetches pages from the official Kubernetes documentation sitemap, extracts main article text, and writes `.md`, `.txt`, and `.docx` files under `data/` (relative to the repo root). Uses polite delays and respects common crawl constraints (e.g. skips disallowed API reference paths except allowlisted).

**Typical use:** build a small, diverse corpus for local RAG testing.

**Dependencies:** `beautifulsoup4`, `html2text`, `python-docx`, `certifi` (see script imports).
