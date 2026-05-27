import llm

test_cases = [
    ("hello", "GREETING"),
    ("what is machine learning?", "ML QUESTION"),
    ("what is python?", "PYTHON QUESTION"),
    ("how to use this system?", "HOW-TO"),
    ("Review this response for quality", "CRITIC"),
]

for test, label in test_cases:
    print(f"\n{'='*60}")
    print(f"{label}")
    print(f"Q: {test}")
    print(f"{'='*60}")
    response = llm.generate_mock_response(test)
    print(f"A: {response[:180]}...")
