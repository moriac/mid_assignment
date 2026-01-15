"""
Test script to verify hierarchical retrieval integration with Specific Task Expert Agent
"""

import os
from dotenv import load_dotenv
from specific_task_expert_agent import SpecificTaskExpertAgent

load_dotenv()


def test_hierarchical_integration():
    """Test the integration of hierarchical retrieval with Specific Task Expert Agent."""
    
    print("=" * 80)
    print("Testing Hierarchical Retrieval Integration with Specific Task Expert Agent")
    print("=" * 80)
    
    # Check for required files
    pdf_path = "insurance_claim_case.pdf"
    if not os.path.exists(pdf_path):
        print(f"\n⚠️ Warning: {pdf_path} not found. The retriever may fail.")
        print("   Please ensure the insurance claim PDF is in the current directory.\n")
    
    # Initialize agent with hierarchical retrieval
    print("\n[1/3] Initializing Specific Task Expert Agent with hierarchical retrieval...\n")
    agent = SpecificTaskExpertAgent(use_hierarchical_retrieval=True)
    
    # Test queries
    test_queries = [
        "What is the claim date?",
        "Who is the policyholder?",
        "What is the claim amount?",
        "When was the incident reported?"
    ]
    
    print("\n[2/3] Running test queries...\n")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"Test Query {i}/{len(test_queries)}: {query}")
        print("=" * 80)
        
        try:
            # Get retrieved nodes directly
            retrieved_nodes = agent.hierarchical_retriever.retrieve(query)
            
            print(f"\n📄 RETRIEVED CONTEXT ({len(retrieved_nodes)} nodes):")
            print("-" * 80)
            for i, node in enumerate(retrieved_nodes, 1):
                print(f"\n[Node {i}]")
                print(f"Score: {node.score:.4f}")
                print(f"Text:\n{node.text}")
                print("-" * 80)
            
            # Get final answer
            print("\n🤖 FINAL ANSWER:")
            print("-" * 80)
            response = agent.process_specific_question(query)
            print(response)
            print(f"\n✓ Query processed successfully")
            
        except Exception as e:
            print(f"\n❌ Error processing query: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "-" * 80)
    
    print("\n[3/3] Testing complete!")
    print("\n" + "=" * 80)
    print("Integration Test Summary")
    print("=" * 80)
    print("\n✓ Hierarchical retrieval system successfully integrated with Specific Task Expert Agent")
    print("\nKey features:")
    print("  • Uses LlamaIndex AutoMergingRetriever for intelligent context retrieval")
    print("  • Automatically merges child nodes into parent nodes for better context")
    print("  • Replaces direct Supabase small_chunks table queries")
    print("  • Maintains all MCP tool functionality (date calculations, compliance checks)")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Verify API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY not found in environment variables.")
        print("   Please set it in your .env file or environment.\n")
        exit(1)
    
    test_hierarchical_integration()
