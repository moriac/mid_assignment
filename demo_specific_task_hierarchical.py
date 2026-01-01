"""
Simple example demonstrating the hierarchical retrieval integration
with the Specific Task Expert Agent.

This script shows how to use the enhanced agent for precise question answering.
"""

import os
from dotenv import load_dotenv
from specific_task_expert_agent import SpecificTaskExpertAgent

load_dotenv()


def main():
    """Run a simple demonstration of the hierarchical integration."""
    
    print("\n" + "=" * 80)
    print("Specific Task Expert Agent - Hierarchical Retrieval Demo")
    print("=" * 80)
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY not found.")
        print("Please set it in your .env file.")
        return
    
    # Initialize the agent
    print("\n[1] Initializing agent with hierarchical retrieval...")
    agent = SpecificTaskExpertAgent(use_hierarchical_retrieval=True)
    
    # Example queries
    queries = [
        "What is the claim number?",
        "When did the incident occur?",
        "What is the total claim amount?",
        "How many days elapsed between the incident date and when the claim was filed?",
    ]
    
    print("\n[2] Processing example queries...\n")
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'─' * 80}")
        print(f"Query {i}: {query}")
        print('─' * 80)
        
        try:
            # Process the query
            response = agent.process_specific_question(query)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("Demo complete!")
    print("=" * 80)
    print("\nKey features demonstrated:")
    print("  ✓ Hierarchical auto-merging retrieval")
    print("  ✓ Precise answer extraction")
    print("  ✓ Intelligent context assembly")
    print("\nFor more details, see: SPECIFIC_TASK_HIERARCHICAL_INTEGRATION.md")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
