from prometheus_client import Counter
from prometheus_client import Histogram

REQUEST_COUNT = Counter(
    "llm_requests_total",
    "Total LLM Requests"
)

TOKENS = Counter("llm_tokens_total", "Total tokens used")

ERROR_COUNT = Counter("llm_errors_total", "Total LLM Errors")

MODEL_USAGE = Counter("llm_model_calls_total", "Model usage", ["model_name"])

LATENCY = Histogram(
    "llm_latency_seconds",
    "LLM Latency"
)