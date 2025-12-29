"""
Interactive Query Interface for Hierarchical Auto-Merging Retriever

Run this script to send queries and see the retrieved nodes.
"""

import sys
from hierarchical_retriever import get_claim_retriever


def display_nodes(nodes, query):
    """Display retrieved nodes in a readable format."""
    print("\n" + "=" * 70)
    print(f"QUERY: {query}")
    print("=" * 70)
    print(f"\nRetrieved {len(nodes)} node(s) after auto-merging:\n")
    
    for i, node in enumerate(nodes, 1):
        print(f"{'─' * 70}")
        print(f"[Node {i}] Score: {node.score:.4f} | Length: {len(node.text)} chars")
        print(f"{'─' * 70}")
        print(node.text)
        print()
    
    print("=" * 70 + "\n")


def main():
    """Interactive query interface."""
    print("\n" + "=" * 70)
    print("HIERARCHICAL AUTO-MERGING RETRIEVER - INTERACTIVE QUERY")
    print("=" * 70)
    print("\nInitializing retriever (this may take a moment)...")
    
    try:
        retriever = get_claim_retriever()
        print("✓ Retriever ready!\n")
    except Exception as e:
        print(f"\n✗ Error initializing retriever: {e}")
        print("\nMake sure:")
        print("1. You're in the virtual environment")
        print("2. All dependencies are installed")
        print("3. insurance_claim_case.pdf exists")
        return
    
    print("=" * 70)
    print("You can now send queries to retrieve relevant information.")
    print("Type 'quit', 'exit', or 'q' to stop.")
    print("=" * 70 + "\n")
    
    # Example queries to help user get started
    example_queries = [
        "What is the claim date?",
        "What damages were reported?",
        "Who is the claimant?",
        "Summarize the incident",
    ]
    
    print("Example queries you can try:")
    for i, example in enumerate(example_queries, 1):
        print(f"  {i}. {example}")
    print()
    
    query_count = 0
    
    while True:
        try:
            # Get user input
            query = input("Enter your query (or 'quit' to exit): ").strip()
            
            # Check for exit commands
            if query.lower() in ['quit', 'exit', 'q', '']:
                print("\nGoodbye! 👋\n")
                break
            
            query_count += 1
            
            print(f"\n🔍 Searching for: '{query}'...")
            
            # Retrieve nodes
            nodes = retriever.retrieve(query)
            
            # Display results
            display_nodes(nodes, query)
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye! 👋\n")
            break
        except Exception as e:
            print(f"\n✗ Error processing query: {e}\n")
            import traceback
            traceback.print_exc()
    
    print(f"\nTotal queries processed: {query_count}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
