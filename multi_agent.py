"""LangGraph Multi-Agent Workflow"""
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
import time

from telemetry import tracer
from metrics import REQUEST_COUNT, LATENCY
from llm import ask_llm


class AgentState(TypedDict):
    """State for multi-agent workflow"""
    query: str
    query_type: str  # "simple", "research", "complex"
    analysis: str
    research_data: str
    response: str
    latency: float


def query_analyzer(state: AgentState) -> AgentState:
    """Determine the type of query"""
    with tracer.start_as_current_span("query-analyzer"):
        prompt = f"""Classify this query as:
- "simple" (straightforward question)
- "research" (needs external info/data)
- "complex" (needs multi-step reasoning)

Query: {state['query']}

Respond with just the classification word."""
        
        classification = ask_llm(prompt).strip().lower()
        
        # Validate classification
        if classification not in ["simple", "research", "complex"]:
            classification = "simple"
        
        state["query_type"] = classification
        state["analysis"] = f"Classified as: {classification}"
    
    return state


def research_agent(state: AgentState) -> AgentState:
    """Gather additional context if needed"""
    with tracer.start_as_current_span("research-agent"):
        if state["query_type"] in ["research", "complex"]:
            prompt = f"""Provide relevant context for this query:
Query: {state['query']}

Give concise background information."""
            
            state["research_data"] = ask_llm(prompt)
        else:
            state["research_data"] = ""
    
    return state


def response_generator(state: AgentState) -> AgentState:
    """Generate final response"""
    with tracer.start_as_current_span("response-generator"):
        start = time.time()
        
        context = f"Context: {state['research_data']}" if state["research_data"] else ""
        
        prompt = f"""Answer this query:
{state['query']}
{context}

Provide a clear, helpful response."""
        
        state["response"] = ask_llm(prompt)
        state["latency"] = time.time() - start
        LATENCY.observe(state["latency"])
    
    return state


def should_research(state: AgentState) -> Literal["research_agent", "response_generator"]:
    """Route to research if needed"""
    return "research_agent" if state["query_type"] in ["research", "complex"] else "response_generator"


# Build and compile graph
_workflow = StateGraph(AgentState)
_workflow.add_node("analyzer", query_analyzer)
_workflow.add_node("research_agent", research_agent)
_workflow.add_node("response_generator", response_generator)

_workflow.add_edge(START, "analyzer")
_workflow.add_conditional_edges("analyzer", should_research)
_workflow.add_edge("research_agent", "response_generator")
_workflow.add_edge("response_generator", END)

_multi_agent_app = _workflow.compile()


def run_multi_agent(query: str) -> str:
    """Run multi-agent workflow"""
    REQUEST_COUNT.inc()
    
    with tracer.start_as_current_span("multi-agent-workflow"):
        result = _multi_agent_app.invoke({
            "query": query,
            "query_type": "",
            "analysis": "",
            "research_data": "",
            "response": "",
            "latency": 0.0
        })
    
    return result["response"]
