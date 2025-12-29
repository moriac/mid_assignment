"""
Integration Example: Using Hierarchical Retriever with Existing Agents

This script demonstrates how to integrate the hierarchical auto-merging retriever
with the existing agent architecture in this project.
"""

import os
from hierarchical_retriever import get_claim_retriever
from llama_index.core.query_engine import RetrieverQueryEngine


def example_1_basic_retrieval():
    """Example 1: Basic retrieval with the hierarchical retriever."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Hierarchical Retrieval")
    print("=" * 70 + "\n")
    
    # Get the retriever
    retriever = get_claim_retriever()
    
    # Query for specific information
    query = "What is the claim date and claim number?"
    print(f"Query: {query}\n")
    
    # Retrieve nodes
    nodes = retriever.retrieve(query)
    
    print(f"Retrieved {len(nodes)} node(s) with auto-merging:\n")
    
    for i, node in enumerate(nodes, 1):
        print(f"[Node {i}] Score: {node.score:.4f}")
        print(f"Text: {node.text[:300]}...\n")
    
    return nodes


def example_2_query_engine():
    """Example 2: Using with a query engine for natural language responses."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Query Engine Integration")
    print("=" * 70 + "\n")
    
    # Get the retriever and wrap it in a query engine
    retriever = get_claim_retriever()
    query_engine = RetrieverQueryEngine.from_args(retriever)
    
    # Ask natural language questions
    questions = [
        "What is the claim number?",
        "When did the incident occur?",
        "Summarize the key details of this insurance claim"
    ]
    
    for question in questions:
        print(f"Q: {question}")
        response = query_engine.query(question)
        print(f"A: {response}\n")
        print("-" * 70 + "\n")


def example_3_agent_integration():
    """Example 3: Integration with existing agent pattern."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Agent Integration Pattern")
    print("=" * 70 + "\n")
    
    from llama_index.llms.openai import OpenAI
    
    # Set up components
    retriever = get_claim_retriever()
    llm = OpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))
    
    # Agent-like workflow
    def process_claim_query(user_query: str) -> str:
        """
        Agent-like function that uses hierarchical retrieval.
        
        This pattern can be integrated into your existing agents:
        - OrchestratorAgent
        - SpecificTaskExpertAgent
        - SummarizationExpertAgent
        """
        # Step 1: Retrieve relevant context
        print(f"🔍 Retrieving context for: '{user_query}'")
        nodes = retriever.retrieve(user_query)
        
        # Step 2: Combine retrieved context
        context = "\n\n".join([node.text for node in nodes])
        print(f"✓ Retrieved {len(nodes)} context chunk(s)\n")
        
        # Step 3: Build prompt with context
        prompt = f"""Based on the following context from an insurance claim document, 
answer the user's question accurately and concisely.

Context:
{context}

Question: {user_query}

Answer:"""
        
        # Step 4: Get LLM response
        print("💬 Generating response...")
        response = llm.complete(prompt)
        
        return str(response)
    
    # Test the agent workflow
    test_queries = [
        "What type of insurance claim is this?",
        "Are there any dates mentioned in the claim?"
    ]
    
    for query in test_queries:
        print(f"\nUser Query: {query}")
        print("-" * 70)
        answer = process_claim_query(query)
        print(f"\nAgent Response:\n{answer}\n")
        print("=" * 70)


def example_4_comparison_with_simple_retrieval():
    """Example 4: Compare with simple retrieval approach."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Hierarchical vs. Simple Retrieval")
    print("=" * 70 + "\n")
    
    from supabase_utils import get_top_k_chunks_from_small_chunks
    
    query = "claim date"
    
    # Hierarchical retrieval
    print("Hierarchical Auto-Merging Retrieval:")
    print("-" * 70)
    retriever = get_claim_retriever()
    hierarchical_nodes = retriever.retrieve(query)
    
    print(f"Retrieved {len(hierarchical_nodes)} node(s)")
    print(f"Total characters: {sum(len(n.text) for n in hierarchical_nodes)}")
    print(f"Average score: {sum(n.score for n in hierarchical_nodes) / len(hierarchical_nodes):.4f}")
    
    if hierarchical_nodes:
        print(f"\nSample (first 200 chars):")
        print(f"{hierarchical_nodes[0].text[:200]}...\n")
    
    # Simple retrieval (if small_chunks table exists)
    print("\nSimple Retrieval (from small_chunks):")
    print("-" * 70)
    try:
        simple_chunks = get_top_k_chunks_from_small_chunks(query, k=6)
        print(f"Retrieved {len(simple_chunks)} chunk(s)")
        print(f"Total characters: {sum(len(c) for c in simple_chunks)}")
        
        if simple_chunks:
            print(f"\nSample (first 200 chars):")
            print(f"{simple_chunks[0][:200]}...\n")
    except Exception as e:
        print(f"⚠ Simple retrieval not available: {e}")
        print("(This is expected if small_chunks table doesn't have data)\n")
    
    print("Key Difference:")
    print("- Hierarchical: Auto-merges small chunks into larger context")
    print("- Simple: Returns fixed-size chunks")
    print("- Hierarchical: Better for queries needing broader context")


def example_5_custom_configuration():
    """Example 5: Custom retriever configuration."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Custom Configuration")
    print("=" * 70 + "\n")
    
    from hierarchical_retriever import HierarchicalClaimRetriever
    
    # Create a custom retriever with different settings
    print("Creating custom retriever with larger chunks...")
    
    custom_retriever = HierarchicalClaimRetriever(
        pdf_path="insurance_claim_case.pdf",
        table_name="hierarchical_chunks",
        chunk_sizes=[4096, 1024, 256]  # Larger chunks for more context
    )
    
    # Build (note: this would create a different index)
    # Commented out to avoid overwriting the default index
    # retriever = custom_retriever.build_all()
    
    print("Custom configuration:")
    print(f"  Chunk sizes: {custom_retriever.chunk_sizes}")
    print(f"  PDF path: {custom_retriever.pdf_path}")
    print(f"  Table name: {custom_retriever.table_name}")
    print("\nTo use custom chunk sizes, uncomment the build_all() call above.")


def main():
    """Run all integration examples."""
    print("\n" + "=" * 70)
    print("HIERARCHICAL RETRIEVER - INTEGRATION EXAMPLES")
    print("=" * 70)
    
    examples = [
        ("Basic Retrieval", example_1_basic_retrieval),
        ("Query Engine", example_2_query_engine),
        ("Agent Integration", example_3_agent_integration),
        ("Comparison", example_4_comparison_with_simple_retrieval),
        ("Custom Config", example_5_custom_configuration),
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nRunning all examples...\n")
    
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n⚠ Example '{name}' encountered an error: {e}\n")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✓ Integration examples completed!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Integrate these patterns into your existing agents")
    print("2. Customize chunk sizes for your use case")
    print("3. Experiment with different similarity_top_k values")
    print("4. Compare results with your existing retrieval methods")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user.")
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure you have:")
        print("1. Installed all dependencies (pip install -r requirements.txt)")
        print("2. Set up .env with required credentials")
        print("3. Run the Supabase SQL setup script")
        print("4. Ensured insurance_claim_case.pdf exists")
