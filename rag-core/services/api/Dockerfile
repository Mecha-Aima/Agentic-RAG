# Build from repository root: rag-core/
#   docker build -f services/api/Dockerfile -t rag-api:latest .
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY services/api/requirements.txt ./services/api/requirements.txt
RUN pip install --no-cache-dir -r ./services/api/requirements.txt

COPY services/api/ ./services/api/
COPY libs/ ./libs/

EXPOSE 8000
CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
