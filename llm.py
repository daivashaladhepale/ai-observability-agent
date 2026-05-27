import requests
import sys
import os
from telemetry import tracer

# Use mock LLM if MOCK_LLM env var is set (for testing without Ollama)
# Default to REAL Ollama mode - set to "true" to use mock
MOCK_LLM = os.getenv("MOCK_LLM", "false").lower() == "true"

def generate_mock_response(prompt: str) -> str:
    """Smart context-aware mock LLM - detects query type and responds accordingly"""
    prompt_lower = prompt.lower()
    
    # Extract the actual user query if this is from an agent
    user_query = prompt
    if "query:" in prompt_lower:
        # Extract text after "Query:"
        user_query = prompt.split("Query:")[-1].split("\n")[0].strip()
    
    user_query_lower = user_query.lower().strip()
    
    # ===== SIMPLE GREETINGS =====
    if user_query_lower in ['hi', 'hello', 'hey', 'hello!', 'hi!', 'hey there']:
        return "Hello! I'm your AI assistant. How can I help you today?"
    
    if user_query_lower in ['thanks', 'thank you', 'thanks!']:
        return "You're welcome! Is there anything else I can help with?"
    
    # ===== AGENT-SPECIFIC RESPONSES =====
    
    # PLANNER: Detect planning requests from Planner agent
    if "plan" in prompt_lower and "query:" in prompt_lower and len(user_query) > 5:
        return f"""Execution Plan for '{user_query}':
1. Analyze and understand the query
2. Identify key information needed
3. Gather relevant data
4. Structure findings
5. Generate response"""
    
    # RESEARCH: Detect research requests
    if "research" in prompt_lower or "gather" in prompt_lower:
        return """Research Findings:
• Current best practices and methodologies
• Industry standards and trends
• Real-world applications and examples
• Case studies and successful implementations"""
    
    # CLASSIFICATION: Classify query type
    if "classify" in prompt_lower:
        if len(user_query) < 20:
            return "Classification: simple"
        elif "how" in user_query_lower or "what" in user_query_lower:
            return "Classification: informational"
        else:
            return "Classification: general"
    
    # CRITIC/REVIEW: Detect review/validation
    if "review" in prompt_lower or "enhance" in prompt_lower or "validate" in prompt_lower:
        return """Quality Assessment:
Strengths: Clear content structure, comprehensive coverage
Areas for improvement: Add specific examples, strengthen details
Recommendation: Response is valid and well-formed"""
    
    # ===== USER QUERIES =====
    
    # "What is" questions
    if "what is" in user_query_lower or "explain" in user_query_lower:
        if "machine learning" in user_query_lower:
            return "Machine Learning is a subset of AI that enables systems to learn from data. Types: Supervised (labeled data), Unsupervised (pattern finding), Reinforcement (reward-based). Used in recommendations, predictions, automation, and more."
        elif "python" in user_query_lower:
            return "Python is a high-level, interpreted programming language valued for simplicity and readability. Uses: web development, data science, AI/ML, automation. Key features: dynamic typing, extensive libraries (NumPy, Pandas, TensorFlow)."
        elif "data" in user_query_lower:
            return "Data is raw information collected from various sources. In AI/ML: structured (databases), unstructured (images, text), semi-structured (JSON). Quality data is crucial for training effective models."
        elif "ai" in user_query_lower or "artificial" in user_query_lower:
            return "Artificial Intelligence refers to computer systems designed to perform intelligent tasks. Includes: machine learning, deep learning, NLP, computer vision. Applications: healthcare, finance, transportation, robotics."
        else:
            topic = user_query.replace("what is ", "").replace("explain ", "")
            return f"Definition: {topic} is an important concept with multiple dimensions. Key aspects include foundational principles, practical applications, and current industry trends."
    
    # "How to" questions
    if "how" in user_query_lower:
        if "use" in user_query_lower or "work" in user_query_lower:
            return """Step-by-Step Guide:
1. Understand the fundamentals
2. Set up necessary tools/environment
3. Start with basic examples
4. Practice with real scenarios
5. Optimize and improve your approach"""
        return "Process: First understand requirements → Plan approach → Gather resources → Implement → Test → Refine based on feedback"
    
    # Default responses
    if len(user_query) > 3:
        return f"Response: Based on your inquiry regarding '{user_query}', this is an important topic. Key aspects: understanding core concepts, exploring applications, evaluating trade-offs, considering implications."
    
    return "Hello! I'm ready to help. What would you like to know?"

def ask_llm(prompt: str):
    from opentelemetry import trace as otel_trace
    
    # Get current span and add attributes
    current_span = otel_trace.get_current_span()
    
    # Add prompt to span (truncate if too long)
    prompt_display = prompt[:200] if len(prompt) > 200 else prompt
    current_span.set_attribute("llm.prompt", prompt_display)
    current_span.set_attribute("llm.prompt_length", len(prompt))
    
    # Use mock if enabled
    if MOCK_LLM:
        print(f"[DEBUG] Using MOCK LLM mode", file=sys.stderr)
        response = generate_mock_response(prompt)
        # Add response to span
        response_display = response[:200] if len(response) > 200 else response
        current_span.set_attribute("llm.response", response_display)
        current_span.set_attribute("llm.response_length", len(response))
        current_span.set_attribute("llm.model", "mock")
        return response
    
    try:
        print(f"[DEBUG] Attempting to connect to Ollama at http://localhost:11434/api/generate", file=sys.stderr)
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            },
            timeout=180  # INCREASED: 180 seconds (3 minutes) for complex queries
        )
        print(f"[DEBUG] Got response status: {response.status_code}", file=sys.stderr)
        result = response.json()["response"]
        print(f"[DEBUG] Got LLM response: {result[:100]}", file=sys.stderr)
        
        # Add response to span
        response_display = result[:200] if len(result) > 200 else result
        current_span.set_attribute("llm.response", response_display)
        current_span.set_attribute("llm.response_length", len(result))
        current_span.set_attribute("llm.model", "mistral")
        current_span.set_attribute("llm.status", "success")
        
        return result
    except requests.exceptions.Timeout:
        print(f"[WARN] Ollama timeout after 180s. Using mock response.", file=sys.stderr)
        response = generate_mock_response(prompt)
        current_span.set_attribute("llm.status", "timeout_fallback")
        current_span.set_attribute("llm.model", "mock")
        return response
    except Exception as e:
        print(f"[ERROR] Exception in ask_llm: {type(e).__name__}: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        # Fallback: Use mock response instead of error message
        print(f"[INFO] Falling back to mock LLM response", file=sys.stderr)
        return generate_mock_response(prompt)