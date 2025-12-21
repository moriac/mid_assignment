"""
Demonstration of Summarization Expert with Supabase Retrieval
"""

from orchestrator_agent import OrchestratorAgent

def main():
    print("=" * 60)
    print("Orchestrator Agent with Enhanced Summarization Expert")
    print("=" * 60)
    print("\nThe Summarization Expert now:")
    print("✅ Retrieves top 3 relevant chunks from Supabase")
    print("✅ Adds retrieved context to the LLM prompt")
    print("✅ Returns comprehensive answers based on the PDF content\n")
    
    # Initialize the orchestrator
    print("Initializing agent...")
    orchestrator = OrchestratorAgent()
    
    # Test with a broad question
    test_question = "Give me a summary of the insurance claim"
    
    print("\n" + "=" * 60)
    print(f"Testing with: '{test_question}'")
    print("=" * 60)
    
    # Process the question
    result = orchestrator.run(test_question)
    
    print("\n" + result)
    print("\n" + "=" * 60)
    print("✨ Demonstration Complete!")
    print("=" * 60)
    print("\n📊 How it works:")
    print("1. Orchestrator classifies the question (Type 2 - Broad)")
    print("2. Routes to Summarization Expert Agent")
    print("3. Summarization Expert retrieves top 3 chunks from 'summary_chunks' table")
    print("4. LLM receives the question + retrieved context")
    print("5. LLM generates comprehensive answer")
    print("6. Answer is returned to Orchestrator and printed\n")

if __name__ == "__main__":
    main()
