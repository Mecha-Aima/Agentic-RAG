# pipelines/jobs/s3_event_handler.py
import json
import os
import shlex
import urllib.error
import urllib.request
from typing import Any, Dict


def _submit_ray_job_http(entrypoint: str, runtime_env: Dict[str, Any]) -> str:
    base = os.getenv("RAY_ADDRESS", "http://127.0.0.1:8265").rstrip("/")
    url = f"{base}/api/jobs/"
    payload: Dict[str, Any] = {
        "entrypoint": entrypoint,
        "runtime_env": runtime_env,
        "job_id": None,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ray job API HTTP {e.code}: {err_body}") from e
    job_id = data.get("job_id") or data.get("submission_id")
    return str(job_id) if job_id else json.dumps(data)


def handle_s3_event(event: Dict[str, Any], context: Any) -> None:
    """
    Lambda entry point: S3 ObjectCreated -> Ray job submission.
    """
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        print(f"File uploaded: s3://{bucket}/{key}")
        submit_ingestion_job(bucket, key)


def submit_ingestion_job(bucket: str, file_key: str) -> str:
    """
    POST to Ray Job Submission API (no ray package in Lambda).
    Requires rag-core synced to RAG_CODE_ROOT on the EC2 host and a .env there
    (DATABASE_URL, NEO4J_*, QDRANT_*, GROQ_API_KEY, AWS creds as needed).
    """
    rag_root = os.getenv("RAG_CODE_ROOT", "/opt/rag-core")
    py = os.getenv("PYTHON_BIN", "python3.11")
    env_file = f"{rag_root}/.env"
    env_q = shlex.quote(env_file)
    rag_q = shlex.quote(rag_root)
    bucket_q = shlex.quote(bucket)
    key_q = shlex.quote(file_key)

    entrypoint = (
        f"bash -lc 'set -a && [ -f {env_q} ] && . {env_q}; set +a && "
        f"export PYTHONPATH={rag_q} && cd {rag_q} && "
        f"{py} pipelines/ingestion/main.py {bucket_q} {key_q}'"
    )

    runtime_env = {
        "pip": [
            "boto3>=1.34",
            "qdrant-client==1.7.3",
            "neo4j==5.16.0",
            "langchain==0.1.5",
            "sentence-transformers==2.3.1",
            "groq>=0.4",
            "httpx>=0.26",
            "unstructured[pdf,docx]==0.11.0",
        ],
    }

    job_id = _submit_ray_job_http(entrypoint, runtime_env)
    print(f"Submitted Ray Job ID: {job_id}")
    return job_id


if __name__ == "__main__":
    fake_event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "rag-docs"},
                    "object": {"key": "manuals/engine_v8.pdf"},
                }
            }
        ]
    }
    handle_s3_event(fake_event, None)
