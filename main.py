from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# IMPORTANT: Import telemetry FIRST to initialize Jaeger tracing
import telemetry  # This sets up the tracer and connects to Jaeger
from telemetry import tracer

from agentic_multi_agent import run_multi_agent_workflow

from prometheus_client import generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
from metrics import REQUEST_COUNT

from fastapi.responses import Response

# Instrument FastAPI to auto-trace all endpoints
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()

# Instrument FastAPI to auto-trace all HTTP endpoints
FastAPIInstrumentor.instrument_app(app)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:5175", "http://127.0.0.1:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "ai-observability-agent"}

@app.get("/chat")
def chat(q: str):
    """Chat endpoint - runs agentic workflow with timeout handling"""
    # Increment request counter
    REQUEST_COUNT.inc()
    
    # Create root span for this chat request
    with tracer.start_as_current_span("chat-request") as root_span:
        root_span.set_attribute("chat.query", q[:200])  # Truncate long queries
        
        if not q or len(q.strip()) == 0:
            return {"response": "Please provide a query", "agent_workflow": []}
        
        try:
            response, agent_logs = run_multi_agent_workflow(q)
            root_span.set_attribute("chat.status", "success")
            return {
                "response": response,
                "agent_workflow": agent_logs,
                "status": "success"
            }
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            root_span.set_attribute("chat.status", "error")
            root_span.set_attribute("chat.error", error_msg)
            return {
                "response": error_msg,
                "agent_workflow": [f"[ERROR] {error_msg}"],
                "status": "error"
            }

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )