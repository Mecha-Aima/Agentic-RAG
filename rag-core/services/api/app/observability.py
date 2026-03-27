import logging

from fastapi import FastAPI

from libs.observability.tracing import configure_tracing

logger = logging.getLogger(__name__)


def setup_observability(app: FastAPI) -> None:
    """
    JSON logs to stdout for CloudWatch (no OTLP / Jaeger on free tier).
    """
    configure_tracing(service_name="rag-api-service")
    logger.info("Observability: structured logging to stdout enabled.")
