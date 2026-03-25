from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from libs.observability.tracing import configure_tracing

def setup_observability(app: FastAPI):
    """
    Configures and attaches OpenTelemetry to the FastAPI app
    """
    # 1. Configure the tracer (sends data to Jaeger/Datadog)
    configure_tracing(service_name="rag-api-service")

    # 2. Auto-instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)