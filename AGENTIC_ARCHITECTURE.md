# Agentic Multi-Agent Workflow Architecture

## Overview
Real LangGraph multi-agent agentic AI system with specialized agents working collaboratively.

## Agents & Responsibilities

### 1. **Planner Agent**
- Analyzes incoming query
- Creates execution plan
- Determines strategy
- **Tracing**: `agent-planner`

### 2. **Research Agent**
- Identifies research areas from plan
- Gathers external information
- Collects contextual data
- **Tracing**: `agent-research`

### 3. **RAG Agent** (Retrieval-Augmented Generation)
- Searches knowledge base
- Retrieves relevant documents
- Extracts key information
- **Tracing**: `agent-rag`

### 4. **Critic Agent**
- Validates response quality
- Provides feedback
- Refines and enhances response
- **Tracing**: `agent-critic`

## Workflow Flow

```
START
  ↓
[Planner Agent]
  └─ Creates plan for query
      ↓
[Research Agent]
  └─ Gathers external data
      ↓
[Decision Point]
  ├─ If query needs KB lookup → [RAG Agent]
  │   └─ Search & extract documents
  │       ↓
  └─ [Draft Response Generator]
      ├─ Combines: Plan + Research + RAG results
      └─ Generates initial response
          ↓
[Critic Agent]
  ├─ Validates response quality
  ├─ Provides feedback
  └─ Refines/enhances response
      ↓
END (Final Response)
```

## Tools Available to Agents

- `search_knowledge_base(query)` - RAG tool for KB search
- `gather_external_data(topic)` - Research tool for external data
- `validate_response(response)` - Critic tool for quality validation

## Full Tracing

Every step is traced with OpenTelemetry:
- `multi-agent-agentic-workflow` - Main workflow span
- `agent-planner` - Planner execution
- `agent-research` - Research execution
- `agent-rag` - RAG execution
- `agent-draft-generator` - Draft generation
- `agent-critic` - Critic validation
- `tool-*` - Individual tool invocations

## Metrics

- `llm_requests_total` - Total requests counter
- `llm_latency_seconds` - Per-request latency histogram

## State Management

All agents share a unified `AgentState`:
```python
{
    "query": str,              # Original query
    "plan": str,               # Plan from Planner
    "research_data": str,      # Data from Research agent
    "rag_results": str,        # Results from RAG agent
    "draft_response": str,     # Initial response
    "final_response": str,     # Final refined response
    "is_valid": bool,          # Critic validation result
    "feedback": str,           # Critic feedback
    "latency": float,          # Total execution time
    "agent_logs": List[str]    # Activity logs from all agents
}
```

## Execution

```python
from agentic_multi_agent import run_multi_agent_workflow

response, agent_logs = run_multi_agent_workflow("What is machine learning?")

# Returns:
# - response: Final refined response
# - agent_logs: Activity log from each agent
```

## Key Features

✅ **True Multi-Agent Architecture** - Multiple specialized agents
✅ **Conditional Routing** - Dynamic path based on query type
✅ **Tool Integration** - Agents have access to tools (RAG, search, etc.)
✅ **Full Observability** - Tracing per agent + metrics
✅ **State Sharing** - All agents access unified state
✅ **Quality Validation** - Critic agent ensures response quality
✅ **Agentic Workflow** - Agents make decisions, not just sequential steps

## API Response

```json
{
    "response": "Final refined answer from Critic agent",
    "agent_workflow": [
        "[PLANNER] Plan created: ...",
        "[RESEARCH] Gathered data on: ...",
        "[RAG] Retrieved and processed documents",
        "[DRAFT] Generated initial response",
        "[CRITIC] Response validated and enhanced"
    ]
}
```
