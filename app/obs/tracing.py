from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from sqlalchemy.ext.asyncio import AsyncEngine


def instrument(
    app: FastAPI,
    async_engine: AsyncEngine,
    *,
    export_url: str = "http://localhost:4317",
    app_name: str = "fastapiapp",
    compose_service: str | None = None,
    log_correlation: bool = True,
) -> None:
    # Set the service name to show in traces
    compose_service = compose_service or app_name
    resource = Resource.create(
        attributes={
            "service.name": app_name,
            "compose_service": compose_service,
        }
    )
    # Set the tracer provider
    tracer = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer)
    tracer.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=export_url))
    )
    # Set the logging format
    if log_correlation:
        LoggingInstrumentor().instrument(
            tracer_provider=tracer, set_logging_format=True
        )
    # Instrument
    HTTPXClientInstrumentor().instrument(tracer_provider=tracer)
    SQLAlchemyInstrumentor().instrument(
        engine=async_engine.sync_engine, tracer_provider=tracer
    )
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)
