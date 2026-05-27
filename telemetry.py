from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create resource with service name
resource = Resource.create({"service.name": "ai-observability-agent"})

# Create tracer provider with resource
trace_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(trace_provider)

tracer = trace.get_tracer(__name__)

# Only export traces if Jaeger is enabled (set JAEGER_ENABLED=true to enable)
JAEGER_ENABLED = os.getenv("JAEGER_ENABLED", "false").lower() == "true"

print("\n" + "="*70, file=sys.stderr)
print(f"[TELEMETRY] JAEGER_ENABLED = {JAEGER_ENABLED}", file=sys.stderr)
print(f"[TELEMETRY] Service Name = ai-observability-agent", file=sys.stderr)
print("="*70 + "\n", file=sys.stderr)

if JAEGER_ENABLED:
    try:
        # Use OTLP HTTP exporter - Port 4318 is the standard OTEL HTTP receiver
        otlp_exporter = OTLPSpanExporter(
            endpoint="http://localhost:4318/v1/traces"
        )
        
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        print("\n" + "="*70, file=sys.stderr)
        print("[✓ JAEGER ENABLED] Traces sending to http://localhost:4318/v1/traces", file=sys.stderr)
        print("="*70 + "\n", file=sys.stderr)
    except Exception as e:
        print(f"[WARN] Failed to configure Jaeger: {e}", file=sys.stderr)
else:
    print("[INFO] Jaeger tracing disabled (set JAEGER_ENABLED=true to enable)", file=sys.stderr)