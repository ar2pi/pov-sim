import logging
import os

from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils import get_random_int

# Metrics
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# Logs
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

# Traces
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Flask instrumentation
from opentelemetry.instrumentation.flask import FlaskInstrumentor

OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set up metrics
metric_reader = PeriodicExportingMetricReader(
    # https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html#opentelemetry.exporter.otlp.proto.grpc.metric_exporter.OTLPMetricExporter
    OTLPMetricExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT)
)
meter_provider = MeterProvider(metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)

# Set up logs
logger_provider = LoggerProvider()
set_logger_provider(logger_provider)
logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(
        # https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html#opentelemetry.exporter.otlp.proto.grpc._log_exporter.OTLPLogExporter
        OTLPLogExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT)
    )
)
logging_handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(logging_handler)

# Set up traces
tracer_provider = TracerProvider()
span_processor = BatchSpanProcessor(
    # https://opentelemetry-python.readthedocs.io/en/latest/exporter/otlp/otlp.html#opentelemetry.exporter.otlp.proto.grpc.trace_exporter.OTLPSpanExporter
    OTLPSpanExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT)
)
tracer_provider.add_span_processor(span_processor)
trace.set_tracer_provider(tracer_provider)

app = Flask(__name__)

# Instrument Flask app and system metrics
# https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/flask/flask.html
FlaskInstrumentor().instrument_app(
  app,
  tracer_provider=tracer_provider,
  meter_provider=meter_provider,
)
# https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/logging/logging.html
LoggingInstrumentor().instrument(
  tracer_provider=tracer_provider,
  set_logging_format=True,
  log_level=logging.DEBUG,
)
# https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/system_metrics/system_metrics.html
SystemMetricsInstrumentor().instrument()

Swagger(app)
CORS(app)

# Add a test span to verify tracing
@app.before_request
def before_request():
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("test-span") as span:
        span.set_attribute("test.attribute", "test-value")
        logger.info("Test span created")

# Add a custom metric
meter = metrics.get_meter(__name__)
request_counter = meter.create_counter(
    name="flask_requests_total",
    description="Total number of requests",
    unit="1",
)

@app.before_request
def count_requests():
    request_counter.add(1, {"path": request.path, "method": request.method})

@app.route('/health', methods=['GET'])
def health():
    """Health endpoint
    ---
    responses:
      200:
        description: Returns healthy
    """
    logger.info("Health check endpoint called")
    return jsonify({"status": "healthy"}), 200

@app.route("/", methods=['GET'])
def home():
    """No-op home endpoint
    ---
    responses:
      200:
        description: Returns ok
    """
    return jsonify({"message": "ok"}), 200

@app.route("/flights/<airline>", methods=["GET"])
def get_flights(airline):
    """Get flights endpoint. Optionally, set raise to trigger an exception.
    ---
    parameters:
      - name: airline
        in: path
        type: string
        enum: ["AA", "UA", "DL"]
        required: true
      - name: raise
        in: query
        type: str
        enum: ["500"]
        required: false
    responses:
      200:
        description: Returns a list of flights for the selected airline
    """
    status_code = request.args.get("raise")
    if status_code:
      raise Exception(f"Encountered {status_code} error") # pylint: disable=broad-exception-raised
    random_int = get_random_int(100, 999)
    return jsonify({airline: [random_int]}), 200

@app.route("/flight", methods=["POST"])
def book_flight():
    """Book flights endpoint. Optionally, set raise to trigger an exception.
    ---
    parameters:
      - name: passenger_name
        in: query
        type: string
        enum: ["John Doe", "Jane Doe"]
        required: true
      - name: flight_num
        in: query
        type: string
        enum: ["101", "202", "303", "404", "505", "606"]
        required: true
      - name: raise
        in: query
        type: str
        enum: ["500"]
        required: false
    responses:
      200:
        description: Booked a flight for the selected passenger and flight_num
    """
    status_code = request.args.get("raise")
    if status_code:
      raise Exception(f"Encountered {status_code} error") # pylint: disable=broad-exception-raised
    passenger_name = request.args.get("passenger_name")
    flight_num = request.args.get("flight_num")
    booking_id = get_random_int(100, 999)
    return jsonify({"passenger_name": passenger_name, "flight_num": flight_num, "booking_id": booking_id}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
