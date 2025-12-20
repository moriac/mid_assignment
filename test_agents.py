"""
Test script to demonstrate the Orchestrator with both Expert agents
"""

import os
from orchestrator_agent import OrchestratorAgent

def test_agent():
    """Test the orchestrator agent with different question types."""
    
    # Set API key if available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Please set OPENAI_API_KEY environment variable to run tests.\n")
        return
    
    print("=" * 70)
    print("TESTING ORCHESTRATOR WITH SPECIFIC TASK & SUMMARIZATION EXPERTS")
    print("=" * 70)
    
    # Initialize the orchestrator
    agent = OrchestratorAgent()
    
    # Test cases
    test_questions = [
        ("What was the exact error code in line 45?", 1),  # Expected: Type 1
        ("Who approved the PR on March 5th, 2024?", 1),  # Expected: Type 1
        ("Summarize the key developments in AI this year", 2),  # Expected: Type 2
        ("What happened in the project last month?", 2),  # Expected: Type 2
        ("Give me an overview of the system architecture", 2),  # Expected: Type 2
        ("Hello, how are you?", 3),  # Expected: Type 3
        ("Calculate 25 * 4", 3),  # Expected: Type 3
    ]
    
    for question, expected_type in test_questions:
        print("\n" + "=" * 70)
        print(f"📝 TESTING: {question}")
        print("=" * 70)
        print(f"Expected Type: {expected_type}\n")
        
        response = agent.run(question)
        print(response)
        print("\n")


if __name__ == "__main__":
    test_agent()
