import time

from telemetry import tracer
from metrics import REQUEST_COUNT
from metrics import LATENCY

from llm import ask_llm

def run_agent(query: str):

    REQUEST_COUNT.inc()

    with tracer.start_as_current_span("agent-workflow"):

        with tracer.start_as_current_span("planner-agent"):

            planned_prompt = f"""
            Analyze carefully:
            {query}
            """

        with tracer.start_as_current_span("llm-agent"):

            start = time.time()

            response = ask_llm(planned_prompt)

            LATENCY.observe(
                time.time() - start
            )

        return response