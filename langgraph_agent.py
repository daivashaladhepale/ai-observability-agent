"""LangGraph-based AI Agent with state management"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
import time

from telemetry import tracer
from metrics import REQUEST_COUNT, LATENCY
from llm import ask_llm


class AgentState(TypedDict):
    """State definition for the agent workflow"""
    query: str
    analysis: str
    response: str
    latency: float
    error: str | None


def planner_node(state: AgentState) -> AgentState:
    """Plan and analyze the query"""
    with tracer.start_as_current_span("planner-node"):
        state["analysis"] = f"Analyzing: {state['query']}"
        state["error"] = None
    return state


def llm_node(state: AgentState) -> AgentState:
    """Call the LLM with the analysis"""
    with tracer.start_as_current_span("llm-node"):
        try:
            start = time.time()
            
            prompt = f"""
            Query: {state['query']}
            Analysis: {state['analysis']}
            
            Please provide a detailed response.
            """
            
            response = ask_llm(prompt)
            
            elapsed = time.time() - start
            state["response"] = response
            state["latency"] = elapsed
            
            LATENCY.observe(elapsed)
        except Exception as e:
            state["error"] = str(e)
            state["response"] = f"Error processing query: {str(e)}"
    
    return state


# Create and compile the graph once
_workflow = StateGraph(AgentState)
_workflow.add_node("planner", planner_node)
_workflow.add_node("llm", llm_node)
_workflow.add_edge(START, "planner")
_workflow.add_edge("planner", "llm")
_workflow.add_edge("llm", END)
_agent_app = _workflow.compile()


def run_agent_graph(query: str) -> str:
    """Run the LangGraph agent workflow"""
    REQUEST_COUNT.inc()
    
    # Execute the workflow
    with tracer.start_as_current_span("agent-workflow"):
        result = _agent_app.invoke(
            {"query": query, "analysis": "", "response": "", "latency": 0.0, "error": None}
        )
    
    return result["response"]
