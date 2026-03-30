from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
import logging
from opentelemetry.sdk._logs import LoggingHandler
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, logger
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


def setup_telemetry(service_name: str, otlp_endpoint: str = "http://localhost:4317"):
    resource = Resource({SERVICE_NAME: service_name})
    exporter = OTLPLogExporter(endpoint=otlp_endpoint, insecure=True)

    provider = LoggerProvider(resource=resource)
    provider.add_log_record_processor(BatchLogRecordProcessor(exporter=exporter))
    set_logger_provider(provider)


    handler = LoggingHandler(level=logging.DEBUG, logger_provider=provider)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
    ))
    root_logger.addHandler(console)

    return provider


def setup_tracing(service_name: str, otlp_endpoint: str):
    tracer_provider = TracerProvider(
        resource=Resource.create({SERVICE_NAME: service_name})
    )
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True))
    )
    trace.set_tracer_provider(tracer_provider)
    return tracer_provider

tracer = trace.get_tracer(__name__)


