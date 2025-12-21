"""
Query the Supabase Vector Store
Example script to search through the embedded PDF chunks
"""

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase.client import Client, create_client

# Load environment variables
load_dotenv()


def initialize_supabase() -> Client:
    """Initialize Supabase client"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError(
            "Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env file"
        )
    
    return create_client(supabase_url, supabase_key)


def search_documents(query: str, k: int = 5, table_name: str = "small_chunks"):
    """
    Search for similar documents in the vector store
    
    Args:
        query: The search query
        k: Number of results to return
        table_name: Name of the Supabase table
    """
    print(f"🔍 Searching for: '{query}'")
    print("=" * 60)
    
    # Initialize Supabase client
    supabase_client = initialize_supabase()
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create vector store
    vector_store = SupabaseVectorStore(
        client=supabase_client,
        embedding=embeddings,
        table_name=table_name,
        query_name=f"{table_name}_search"
    )
    
    # Perform similarity search
    results = vector_store.similarity_search_with_relevance_scores(query, k=k)
    
    print(f"\n📄 Found {len(results)} results:\n")
    
    for i, (doc, score) in enumerate(results, 1):
        print(f"Result {i} (Similarity: {score:.4f})")
        print(f"Source: {doc.metadata.get('source_file', 'Unknown')}")
        print(f"Content: {doc.page_content[:200]}...")
        print("-" * 60)
    
    return results


def main():
    """Main function for interactive search"""
    print("=" * 60)
    print("PDF Vector Store Search")
    print("=" * 60)
    print("\nType your search query (or 'quit' to exit)\n")
    
    while True:
        query = input("🔍 Search: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not query:
            continue
        
        try:
            results = search_documents(query, k=5)
            print("\n")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


if __name__ == "__main__":
    # Example usage
    print("Example searches you can try:")
    print("  - Search for specific terms in the PDFs")
    print("  - Ask questions about the content")
    print("  - Look for specific information\n")
    
    main()
