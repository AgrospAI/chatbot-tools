import os
import time

from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource

_resource = Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "fastrag")})
metric_reader = PrometheusMetricReader()
provider = MeterProvider(resource=_resource, metric_readers=[metric_reader])
set_meter_provider(provider)

meter = metrics.get_meter(__name__)

START_TIME = time.time()

http_requests_total = meter.create_counter(
    name="http_requests_total", description="Total HTTP requests", unit="1"
)

http_requests_in_flight = meter.create_up_down_counter(
    name="http_requests_in_flight", description="In-flight HTTP requests", unit="1"
)

http_request_errors_total = meter.create_counter(
    name="http_request_errors_total", description="HTTP request errors", unit="1"
)

requests_per_ip_total = meter.create_counter(
    name="requests_per_ip_total", description="Requests per client IP", unit="1"
)

rejected_requests_total = meter.create_counter(
    name="rejected_requests_total", description="Rejected requests", unit="1"
)

llm_time_to_first_token = meter.create_histogram(
    name="llm_time_to_first_token_seconds", description="Time to first LLM token", unit="s"
)

llm_time_to_last_token = meter.create_histogram(
    name="llm_time_to_last_token_seconds", description="Time to last LLM token", unit="s"
)

llm_question_length = meter.create_histogram(
    name="llm_question_length_chars", description="Question length in characters", unit="1"
)

llm_answer_length = meter.create_histogram(
    name="llm_answer_length_chars", description="Answer length in characters", unit="1"
)

process_start_time_seconds = meter.create_observable_gauge(
    name="process_start_time_seconds",
    callbacks=[lambda options: [metrics.Observation(START_TIME)]],
    description="Process start time",
    unit="s",
)
