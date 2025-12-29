"""
Simple Query Script - Send a query and see retrieved nodes

Usage:
    python simple_query.py "What is the claim date?"
    python simple_query.py "Summarize the damages"
"""

import sys
from hierarchical_retriever import get_claim_retriever


def main():
    # Check if query was provided
    if len(sys.argv) < 2:
        print("\nUsage: python simple_query.py \"your query here\"")
        print("\nExamples:")
        print("  python simple_query.py \"What is the claim date?\"")
        print("  python simple_query.py \"Who is the claimant?\"")
        print("  python simple_query.py \"Summarize the incident\"")
        sys.exit(1)
    
    # Get query from command line
    query = " ".join(sys.argv[1:])
    
    print("\n" + "=" * 70)
    print("HIERARCHICAL RETRIEVER - SIMPLE QUERY")
    print("=" * 70)
    print(f"\nQuery: {query}")
    print("\nInitializing retriever...")
    
    # Get retriever
    retriever = get_claim_retriever()
    
    print(f"\n🔍 Retrieving nodes for: '{query}'...\n")
    
    # Retrieve nodes
    nodes = retriever.retrieve(query)
    
    # Display results
    print("=" * 70)
    print(f"RESULTS: {len(nodes)} node(s) retrieved after auto-merging")
    print("=" * 70 + "\n")
    
    for i, node in enumerate(nodes, 1):
        print(f"[Node {i}]")
        print(f"  Score: {node.score:.4f}")
        print(f"  Length: {len(node.text)} chars")
        print(f"  Node ID: {node.node_id}")
        print(f"\n  Content:")
        print(f"  {'-' * 66}")
        # Print with indentation
        for line in node.text.split('\n'):
            print(f"  {line}")
        print(f"  {'-' * 66}\n")
    
    print("=" * 70)
    print("✓ Query completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
