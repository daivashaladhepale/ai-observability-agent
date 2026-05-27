@echo off
setlocal enabledelayedexpansion
echo Starting AI Observability Platform...
echo.

echo Starting FastAPI backend with Jaeger tracing enabled...
start powershell -Command "cd '%~dp0'; $env:JAEGER_ENABLED='true'; & .\venv\Scripts\Activate.ps1; uvicorn main:app --reload"
timeout /t 2

echo Starting Prometheus...
start cmd /k "cd /d %~dp0\prometheus-3.12.0-rc.0.windows-amd64 && prometheus.exe --config.file=prometheus.yml"
timeout /t 2

echo Starting Jaeger...
start cmd /k "cd /d %~dp0\jaeger-2.18.0-windows-amd64 && jaeger.exe --config-file=..\jaeger-config.yml"
timeout /t 2

echo Starting Grafana...
start cmd /k "cd /d %~dp0\grafana-11.1.5.windows-amd64\bin && grafana-server.exe"
timeout /t 3

echo Starting React frontend...
start cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo All services started!
echo.
echo Frontend: http://localhost:5173
echo FastAPI: http://127.0.0.1:8000
echo Prometheus: http://localhost:9090
echo Grafana: http://localhost:3000
echo Jaeger: http://localhost:16686
echo.
pause
