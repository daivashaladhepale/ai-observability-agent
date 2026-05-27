from prometheus_client import Counter
from prometheus_client import Histogram

REQUEST_COUNT = Counter(
    "llm_requests_total",
    "Total LLM Requests"
)

LATENCY = Histogram(
    "llm_latency_seconds",
    "LLM Latency"
)