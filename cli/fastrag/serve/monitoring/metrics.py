import time

from prometheus_client import Counter, Gauge, Histogram

START_TIME = time.time()

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

http_requests_in_flight = Gauge(
    "http_requests_in_flight",
    "In-flight HTTP requests",
    ["path"],
)

http_request_errors_total = Counter(
    "http_request_errors_total",
    "HTTP request errors",
    ["path", "type"],
)

requests_per_ip_total = Counter(
    "requests_per_ip_total",
    "Requests per client IP",
    ["ip"],
)

rejected_requests_total = Counter(
    "rejected_requests_total",
    "Rejected requests",
    ["reason"],
)

llm_time_to_first_token = Histogram(
    "llm_time_to_first_token_seconds",
    "Time to first LLM token",
    buckets=(0.1, 0.3, 0.5, 1, 2, 5, 10),
)

llm_time_to_last_token = Histogram(
    "llm_time_to_last_token_seconds",
    "Time to last LLM token",
    buckets=(0.5, 1, 2, 5, 10, 30, 60),
)

llm_question_length = Histogram(
    "llm_question_length_chars",
    "Question length in characters",
    buckets=(10, 50, 100, 200, 500, 1000),
)

llm_answer_length = Histogram(
    "llm_answer_length_chars",
    "Answer length in characters",
    buckets=(50, 100, 500, 1000, 2000, 5000),
)

process_start_time_seconds = Gauge(
    "process_start_time_seconds",
    "Process start time",
)
process_start_time_seconds.set(START_TIME)
