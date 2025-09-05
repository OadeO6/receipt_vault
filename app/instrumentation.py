import logging
from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from app.core.connection import sync_engine
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

from app.core.config import settings
# from app.core.logger import CustomLogger

# logger = CustomLogger(__name__)
logger = logging.getLogger(__name__)

resource = Resource.create(
    {
        "service.name": settings.OTEL_SERVICE_NAME,
        "service.version": settings.OTEL_SERVICE_VERSION,
        "service.instance.id": "testing"
    }
)

# Tracer
def initialize_tracer():
    # if not settings.OBSERVABILITY:
    #     logger.warning("Unable to initialize tracer, Observability is not enabled")
    #     return

    tracer_provider = TracerProvider(resource=resource)


    # TODO: handle error if the collector is not available
    otel_span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{settings.OTEL_EXPORTER_OTLP_ENDPOINT}/v1/traces"))
    console_processor = BatchSpanProcessor(ConsoleSpanExporter())
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    SQLAlchemyInstrumentor().instrument(engine=sync_engine)


    tracer_provider.add_span_processor(otel_span_processor)
    # tracer_provider.add_span_processor(console_processor)

    trace.set_tracer_provider(tracer_provider)
    return tracer_provider

initialize_tracer()

def get_tracer():
    if not settings.OBSERVABILITY:
        logger.warning("Unable to get tracer,  Observability is not enabled")
        return None
    tracer = trace.get_tracer(__name__)
    return tracer


# metrics
def initialize_metrics():
    # if not settings.OBSERVABILITY:
    #     logger.warning("Unable to initialize metrics, Observability is not enabled")
    #     return
    otel_metrics_processor = OTLPMetricExporter(endpoint=f"{settings.OTEL_EXPORTER_OTLP_ENDPOINT}/v1/metrics")
    reader = PeriodicExportingMetricReader(otel_metrics_processor)

    metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
    provider = MeterProvider(resource=resource, metric_readers=[reader])

    metrics.set_meter_provider(provider)

initialize_metrics()

# logs
def initialize_logs():
    # if not settings.OBSERVABILITY:
    #     logger.warning("Unable to initialize logs, Observability is not enabled")
    #     return
    provider = LoggerProvider(resource=resource)
    processor = BatchLogRecordProcessor(ConsoleLogExporter())
    otel_processor = BatchLogRecordProcessor(OTLPLogExporter(endpoint=f"{settings.OTEL_EXPORTER_OTLP_ENDPOINT}/v1/logs"))
    provider.add_log_record_processor(processor)
    provider.add_log_record_processor(otel_processor)
    set_logger_provider(provider)
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=provider)
    # logging.getLogger().addHandler(handler)

    return handler

