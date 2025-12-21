"""
Test the updated Summarization Expert Agent with Supabase retrieval
"""

from summarization_expert_agent import SummarizationExpertAgent

def main():
    print("=" * 60)
    print("Testing Summarization Expert with Supabase Retrieval")
    print("=" * 60)
    
    # Initialize the agent
    agent = SummarizationExpertAgent()
    
    # Test questions
    test_questions = [
        "Give me a summary of the insurance claim case",
        "What are the key events in the timeline?",
        "What documentation is missing?"
    ]
    
    for question in test_questions:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print('='*60)
        
        response = agent.process_broad_question(question)
        
        print("\n📋 RESPONSE:")
        print("-" * 60)
        print(response)
        print("-" * 60)
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
