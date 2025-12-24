"""
Test script to verify MCP tools are properly bound to agents.
This will test both agents with questions that should trigger MCP tool usage.
"""

import os
from dotenv import load_dotenv
from specific_task_expert_agent import SpecificTaskExpertAgent
from summarization_expert_agent import SummarizationExpertAgent

load_dotenv()

def test_specific_task_agent_with_tools():
    """Test the Specific Task Expert agent with a date calculation question."""
    print("=" * 70)
    print("TEST 1: Specific Task Expert Agent - Date Calculation Question")
    print("=" * 70)
    
    agent = SpecificTaskExpertAgent()
    
    # Question that should trigger timeline calculation tool
    question = "How long is the duration from 2024-01-15 09:00:00 to 2024-01-20 17:30:00?"
    
    print(f"\n📝 Question: {question}\n")
    print("-" * 70)
    
    response = agent.process_specific_question(question)
    
    print("\n" + "=" * 70)
    print("✅ Test 1 Complete\n")
    

def test_specific_task_agent_without_tools():
    """Test the Specific Task Expert agent with a regular question."""
    print("=" * 70)
    print("TEST 2: Specific Task Expert Agent - Regular Question (No Tools)")
    print("=" * 70)
    
    agent = SpecificTaskExpertAgent()
    
    # Question that should NOT trigger tools
    question = "What is the claim number mentioned in the document?"
    
    print(f"\n📝 Question: {question}\n")
    print("-" * 70)
    
    response = agent.process_specific_question(question)
    
    print("\n" + "=" * 70)
    print("✅ Test 2 Complete\n")


def test_summarization_agent_with_tools():
    """Test the Summarization Expert agent with a business days question."""
    print("=" * 70)
    print("TEST 3: Summarization Expert Agent - Business Days Question")
    print("=" * 70)
    
    agent = SummarizationExpertAgent()
    
    # Question that should trigger business days calculation tool
    question = "How many business days are there from 2024-01-15 to 2024-01-29?"
    
    print(f"\n📝 Question: {question}\n")
    print("-" * 70)
    
    response = agent.process_broad_question(question)
    
    print("\n" + "=" * 70)
    print("✅ Test 3 Complete\n")


def test_summarization_agent_without_tools():
    """Test the Summarization Expert agent with a summary question."""
    print("=" * 70)
    print("TEST 4: Summarization Expert Agent - Summary Question (No Tools)")
    print("=" * 70)
    
    agent = SummarizationExpertAgent()
    
    # Question that should NOT trigger tools
    question = "Give me a summary of the insurance claim"
    
    print(f"\n📝 Question: {question}\n")
    print("-" * 70)
    
    response = agent.process_broad_question(question)
    
    print("\n" + "=" * 70)
    print("✅ Test 4 Complete\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("🧪 TESTING MCP TOOL BINDING IN AGENTS")
    print("=" * 70)
    print("\nThis script tests if the agents properly invoke MCP tools when needed.")
    print("Watch for '🔧 MCP TOOLS USED' messages to confirm tool usage.\n")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
        return
    
    try:
        # Test 1: Specific agent with date calculation (should use tools)
        test_specific_task_agent_with_tools()
        
        # Test 2: Specific agent with regular question (should NOT use tools)
        test_specific_task_agent_without_tools()
        
        # Test 3: Summarization agent with business days (should use tools)
        test_summarization_agent_with_tools()
        
        # Test 4: Summarization agent with summary (should NOT use tools)
        test_summarization_agent_without_tools()
        
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS COMPLETED!")
        print("=" * 70)
        print("\n📊 Summary:")
        print("   - Tests 1 & 3 should show '🔧 MCP TOOLS USED' messages")
        print("   - Tests 2 & 4 should show 'ℹ️  No MCP tools were used' messages")
        print("   - This confirms agents bind to and use MCP tools appropriately\n")
        
    except Exception as e:
        print(f"\n❌ Error running tests: {str(e)}")


if __name__ == "__main__":
    main()
