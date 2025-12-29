"""
Quick Start Example for Hierarchical Auto-Merging Retriever

This script shows the simplest way to use the hierarchical retriever
for querying the insurance claim PDF.
"""

from hierarchical_retriever import get_claim_retriever
from llama_index.core.query_engine import RetrieverQueryEngine


def main():
    """Quick start example."""
    
    print("\n" + "=" * 70)
    print("HIERARCHICAL AUTO-MERGING RETRIEVER - QUICK START")
    print("=" * 70 + "\n")
    
    # Step 1: Get the retriever (this builds everything on first call)
    print("Step 1: Initializing retriever...")
    print("-" * 70)
    retriever = get_claim_retriever()
    
    # Step 2: Create a query engine
    print("\nStep 2: Creating query engine...")
    print("-" * 70)
    query_engine = RetrieverQueryEngine.from_args(retriever)
    print("✓ Query engine ready\n")
    
    # Step 3: Ask some questions
    print("Step 3: Querying the insurance claim...")
    print("=" * 70 + "\n")
    
    questions = [
        "What is the claim number?",
        "When did the incident occur?",
        "What is the total claimed amount?",
        "Summarize the damages claimed",
        "What is the status of the claim?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"Question {i}: {question}")
        print("-" * 70)
        
        # Query the engine
        response = query_engine.query(question)
        
        print(f"Answer: {response}\n")
    
    print("=" * 70)
    print("✓ Quick start example completed!")
    print("=" * 70 + "\n")
    
    # Show how to use just the retriever
    print("\nBonus: Using the retriever directly")
    print("=" * 70)
    
    query = "claim date"
    print(f"\nQuery: '{query}'\n")
    
    nodes = retriever.retrieve(query)
    
    print(f"Retrieved {len(nodes)} node(s) after auto-merging:\n")
    
    for i, node in enumerate(nodes, 1):
        print(f"[Node {i}]")
        print(f"Score: {node.score:.4f}")
        print(f"Length: {len(node.text)} chars")
        print(f"Preview: {node.text[:200]}...")
        print("-" * 70 + "\n")
    
    print("=" * 70)
    print("Next steps:")
    print("1. Try your own questions")
    print("2. Integrate with your agents")
    print("3. Adjust similarity_top_k for different results")
    print("4. See HIERARCHICAL_RETRIEVER_GUIDE.md for more details")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        print("Troubleshooting steps:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Set up .env with OPENAI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY")
        print("3. Run the SQL setup script in Supabase")
        print("4. Ensure insurance_claim_case.pdf exists")
        print("\nFor detailed setup, see: HIERARCHICAL_RETRIEVER_GUIDE.md\n")
        raise
