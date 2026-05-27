# AI Observability Agent 🚀

A production-ready observability platform for monitoring LLM applications with **Metrics**, **Traces**, and **Logs**.

## Features

- 📊 **Metrics**: Real-time metrics tracking with Prometheus & Grafana
- 🔍 **Traces**: Distributed tracing with Jaeger & OpenTelemetry
- ⚡ **FastAPI**: Modern async web framework
- 🤖 **LLM Agent**: Chat endpoint with Ollama integration

## Architecture

```
FastAPI App (8000) → Prometheus (9090) → Grafana (3000)
                  → Jaeger (16686) ← OpenTelemetry
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start All Services
```powershell
# Terminal 1: FastAPI App
uvicorn main:app --reload

# Terminal 2: Prometheus
cd prometheus-3.12.0-rc.0.windows-amd64
.\prometheus.exe --config.file=prometheus.yml

# Terminal 3: Jaeger
cd jaeger-2.18.0-windows-amd64
.\jaeger.exe

# Terminal 4: Grafana
cd grafana-11.1.5.windows-amd64\bin
.\grafana-server.exe
```

### 3. Access Dashboards
- **App**: http://127.0.0.1:8000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Jaeger**: http://localhost:16686

## API Endpoints

- `GET /chat?q=<query>` - Send query to LLM agent
- `GET /metrics` - Prometheus metrics endpoint

## Metrics Tracked

- `llm_requests_total` - Total requests counter
- `llm_latency_seconds` - Request latency histogram

## Tech Stack

- **Framework**: FastAPI, Uvicorn
- **Metrics**: Prometheus, Grafana
- **Tracing**: Jaeger, OpenTelemetry
- **LLM**: Ollama (llama3)
- **Language**: Python 3.10+

## License

MIT
