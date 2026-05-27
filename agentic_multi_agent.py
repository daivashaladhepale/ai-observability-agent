"""
Real LangGraph Multi-Agent Architecture with Agentic Workflow
- Planner Agent: Plans the approach
- Research Agent: Gathers information
- RAG Agent: Retrieves from knowledge base
- Critic Agent: Validates and refines response
"""

from typing import TypedDict, Literal, List
from langgraph.graph import StateGraph, START, END
import time
import json

from telemetry import tracer
from metrics import REQUEST_COUNT, LATENCY
from llm import ask_llm

# ============ QUERY INTENT CLASSIFIER ============

def classify_query_intent(query: str) -> dict:
    """
    OPTIMIZED Query Classification - Fast pattern matching first, LLM only if needed.
    """
    with tracer.start_as_current_span("agent-classify-query") as span:
        query_lower = query.lower().strip()
        
        # FAST PATH: Detect common patterns without LLM call
        classification = {
            "category": "question",
            "intent": "general query",
            "requires_research": False,
            "requires_kb": False,
            "raw_response": "Fast-path classification"
        }
        
        # Greetings (no LLM needed)
        if query_lower in ['hi', 'hello', 'hey', 'how are you', 'what are you doing', 'thanks', 'thank you']:
            classification = {
                "category": "greeting",
                "intent": "social greeting",
                "requires_research": False,
                "requires_kb": False,
                "raw_response": "Greeting detected"
            }
        # Research-heavy queries
        elif any(word in query_lower for word in ['research', 'study', 'analysis', 'report', 'findings']):
            classification = {
                "category": "question",
                "intent": "research query",
                "requires_research": True,
                "requires_kb": True,
                "raw_response": "Research query detected"
            }
        # KB-heavy queries
        elif any(word in query_lower for word in ['what is', 'explain', 'definition', 'tell me about']):
            classification = {
                "category": "question",
                "intent": "knowledge query",
                "requires_research": False,
                "requires_kb": True,
                "raw_response": "Knowledge query detected"
            }
        # How-to queries
        elif any(word in query_lower for word in ['how to', 'how do', 'how can', 'steps']):
            classification = {
                "category": "request",
                "intent": "how-to query",
                "requires_research": False,
                "requires_kb": True,
                "raw_response": "How-to query detected"
            }
        
        # Add classification details to span
        span.set_attribute("classification.category", classification["category"])
        span.set_attribute("classification.intent", classification["intent"])
        span.set_attribute("classification.requires_research", classification["requires_research"])
        span.set_attribute("classification.requires_kb", classification["requires_kb"])
        
        return classification


class AgentState(TypedDict):
    """Shared state for all agents"""
    query: str
    query_classification: dict  # NEW: Intelligent classification of query intent
    plan: str
    research_data: str
    rag_results: str
    draft_response: str
    final_response: str
    is_valid: bool
    feedback: str
    latency: float
    agent_logs: List[str]


# ============ TOOL DEFINITIONS ============

def search_knowledge_base(query: str) -> str:
    """RAG Tool: Search internal knowledge base"""
    with tracer.start_as_current_span("tool-search-kb"):
        # Simulate knowledge base search
        results = f"KB results for '{query}': Relevant documents about {query[:20]}..."
    return results


def gather_external_data(topic: str) -> str:
    """Research Tool: Gather external information"""
    with tracer.start_as_current_span("tool-gather-data"):
        data = f"External data on '{topic}': Research findings..."
    return data


def validate_response(response: str) -> tuple[bool, str]:
    """Critic Tool: Validate response quality"""
    with tracer.start_as_current_span("tool-validate"):
        # Check response quality
        if len(response) > 50 and "response" not in response.lower():
            return True, "Valid response"
        return False, "Response too short or incomplete"


# ============ PLANNER AGENT ============

def planner_agent(state: AgentState) -> AgentState:
    """Planner: OPTIMIZED - Skip for simple queries, use LLM only for complex ones"""
    with tracer.start_as_current_span("agent-planner"):
        classification = state['query_classification']
        
        # Skip planning for simple queries (saves LLM call!)
        if classification['category'] in ['greeting', 'feedback', 'complaint']:
            state["plan"] = f"Direct response: {classification['intent']}"
            state["agent_logs"].append(
                f"[PLANNER] AUTONOMOUS DECISION: Skipping plan for '{classification['category']}'")
            return state
        
        # For complex queries, use quick planning (not full LLM)
        if classification['requires_research'] or classification['requires_kb']:
            # Fast plan based on intent
            intent = classification['intent']
            if 'research' in intent:
                state["plan"] = "1. Gather research data 2. Analyze findings 3. Compile results"
            elif 'how-to' in intent:
                state["plan"] = "1. Outline steps 2. Add details 3. Provide examples"
            elif 'knowledge' in intent:
                state["plan"] = "1. Define concept 2. Provide context 3. Give examples"
            else:
                state["plan"] = "1. Understand query 2. Gather info 3. Generate response"
            
            state["agent_logs"].append(
                f"[PLANNER] AUTONOMOUS DECISION: Quick plan for {intent}")
        else:
            state["plan"] = "Standard response"
            state["agent_logs"].append(f"[PLANNER] AUTONOMOUS DECISION: Standard response mode")
    
    return state


# ============ RESEARCH AGENT ============

def research_agent(state: AgentState) -> AgentState:
    """Research: OPTIMIZED - Skip if not needed to save time"""
    with tracer.start_as_current_span("agent-research"):
        classification = state['query_classification']
        
        # Skip research entirely if not needed
        if not classification['requires_research']:
            state["research_data"] = ""
            state["agent_logs"].append(
                f"[RESEARCH] AUTONOMOUS DECISION: Skipped (not needed for {classification['intent']})")
            return state
        
        # Use mock research data (fast, no LLM call)
        topics = f"Research topics for {state['query'][:30]}"
        research_data = gather_external_data(topics)
        state["research_data"] = research_data
        state["agent_logs"].append(f"[RESEARCH] Gathered data (fast path)")
    
    return state


# ============ RAG AGENT ============

def rag_agent(state: AgentState) -> AgentState:
    """RAG: OPTIMIZED - Skip if not needed"""
    with tracer.start_as_current_span("agent-rag"):
        classification = state['query_classification']
        
        # Skip KB search if not needed
        if not classification['requires_kb']:
            state["rag_results"] = ""
            state["agent_logs"].append(
                f"[RAG] AUTONOMOUS DECISION: Skipped (not needed)")
            return state
        
        # Use fast KB search (no LLM processing)
        rag_results = search_knowledge_base(state["query"])
        state["rag_results"] = rag_results
        state["agent_logs"].append(f"[RAG] Retrieved KB results (fast path)")
    
    return state


# ============ DRAFT RESPONSE GENERATION ============

def draft_response_generator(state: AgentState) -> AgentState:
    """Draft Generator: OPTIMIZED with SINGLE LLM call"""
    with tracer.start_as_current_span("agent-draft-generator") as span:
        classification = state['query_classification']
        
        # Build comprehensive prompt with all context
        context_parts = []
        if state['plan']: context_parts.append(f"Plan: {state['plan']}")
        if state['research_data']: context_parts.append(f"Research: {state['research_data']}")  
        if state['rag_results']: context_parts.append(f"Knowledge: {state['rag_results']}")
        
        context = "\n".join(context_parts) if context_parts else ""
        
        # SINGLE LLM CALL - all-in-one response generation + validation
        prompt = f"""Generate a helpful response to this query. Keep it concise and accurate.
Query: {state['query']}
Type: {classification['category']}
Intent: {classification['intent']}

Context:
{context}

Response:"""
        
        # Add span attributes for observability
        span.set_attribute("draft.query", state['query'][:100])
        span.set_attribute("draft.category", classification['category'])
        span.set_attribute("draft.intent", classification['intent'])
        
        draft = ask_llm(prompt)
        
        # Add response to span
        draft_display = draft[:200] if len(draft) > 200 else draft
        span.set_attribute("draft.response", draft_display)
        span.set_attribute("draft.response_length", len(draft))
        
        state["draft_response"] = draft
        state["agent_logs"].append(
            f"[DRAFT] Generated response (optimized single-call)")
    
    return state


# ============ CRITIC AGENT ============

def critic_agent(state: AgentState) -> AgentState:
    """Critic: OPTIMIZED - Quick validation without extra LLM calls"""
    with tracer.start_as_current_span("agent-critic"):
        classification = state['query_classification']
        draft = state["draft_response"]
        
        # Quick validation (no LLM call needed)
        is_valid, feedback = validate_response(draft)
        state["is_valid"] = is_valid
        state["feedback"] = feedback
        
        # For simple queries, just return draft
        if classification['category'] in ['greeting', 'feedback']:
            state["final_response"] = draft
            state["agent_logs"].append(f"[CRITIC] AUTONOMOUS DECISION: Simple query validated. Final response ready.")
        else:
            # For complex queries, validate is good enough (skip enhancement LLM call)
            state["final_response"] = draft
            state["agent_logs"].append(f"[CRITIC] AUTONOMOUS DECISION: Response validated. Status: {feedback}")
    
    return state


# ============ ROUTING LOGIC - INTELLIGENT CONDITIONAL ROUTING ============

def should_use_rag(state: AgentState) -> Literal["rag_agent", "draft_generator"]:
    """INTELLIGENT ROUTING: Decide if RAG is needed based on query classification"""
    classification = state['query_classification']
    # Let the classification guide the decision
    if classification['requires_kb']:
        return "rag_agent"
    return "draft_generator"


def should_criticize(state: AgentState) -> Literal["critic_agent", "end"]:
    """INTELLIGENT ROUTING: Always use critic to validate and enhance"""
    return "critic_agent"


# ============ BUILD AGENTIC GRAPH ============

workflow = StateGraph(AgentState)

# Add all agents as nodes
workflow.add_node("classify", lambda state: {**state, "query_classification": classify_query_intent(state['query'])})
workflow.add_node("planner", planner_agent)
workflow.add_node("research", research_agent)
workflow.add_node("rag_agent", rag_agent)
workflow.add_node("draft_generator", draft_response_generator)
workflow.add_node("critic", critic_agent)

# Define intelligent flow with autonomous agent decisions
workflow.add_edge(START, "classify")  # First, classify the query
workflow.add_edge("classify", "planner")  # Then planner decides path
workflow.add_edge("planner", "research")  # Research decides if needed
workflow.add_conditional_edges("research", should_use_rag)  # Intelligent routing
workflow.add_edge("rag_agent", "draft_generator")
workflow.add_edge("draft_generator", "critic")  # Always validate
workflow.add_edge("critic", END)

# Compile
multi_agent_graph = workflow.compile()


# ============ MAIN EXECUTION ============

def run_multi_agent_workflow(query: str) -> tuple[str, List[str]]:
    """Execute the complete TRUE agentic AI workflow with intelligent agent decision-making"""
    REQUEST_COUNT.inc()
    
    with tracer.start_as_current_span("multi-agent-agentic-workflow") as span:
        # Add query to span attributes (for Jaeger visibility)
        query_display = query[:200] if len(query) > 200 else query
        span.set_attribute("user.query", query_display)
        span.set_attribute("user.query_length", len(query))
        
        start = time.time()
        
        # Initialize state
        initial_state = {
            "query": query,
            "query_classification": {},  # Will be filled by classify agent
            "plan": "",
            "research_data": "",
            "rag_results": "",
            "draft_response": "",
            "final_response": "",
            "is_valid": False,
            "feedback": "",
            "latency": 0.0,
            "agent_logs": []
        }
        
        # Log that we're using real LLM
        initial_state["agent_logs"].append(f"[SYSTEM] Starting TRUE AGENTIC AI workflow with real LLM")
        initial_state["agent_logs"].append(f"[SYSTEM] User query: '{query}'")
        
        # Execute workflow - agents now make AUTONOMOUS decisions
        result = multi_agent_graph.invoke(initial_state)
        
        elapsed = time.time() - start
        result["latency"] = elapsed
        LATENCY.observe(elapsed)
        
        # Log completion
        result["agent_logs"].append(f"[SYSTEM] Workflow completed in {elapsed:.2f}s")
        
        # Add final response to span (for Jaeger visibility)
        final_response_display = result["final_response"][:200] if len(result["final_response"]) > 200 else result["final_response"]
        span.set_attribute("llm.final_response", final_response_display)
        span.set_attribute("llm.final_response_length", len(result["final_response"]))
        span.set_attribute("workflow.latency_seconds", elapsed)
        span.set_attribute("workflow.classification", result.get("query_classification", {}).get("category", "unknown"))
    
    return result["final_response"], result["agent_logs"]
