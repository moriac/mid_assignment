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
    
    # Create query embedding
    query_embedding = embeddings.embed_query(query)
    
    # Use the similarity search function directly
    results = supabase_client.rpc(
        f"{table_name}_search",
        {
            "query_embedding": query_embedding,
            "match_count": k
        }
    ).execute()
    
    if not results.data:
        print("\n📄 No results found.\n")
        return []
    
    print(f"\n📄 Found {len(results.data)} results:\n")
    
    for i, result in enumerate(results.data, 1):
        print(f"Result {i} (Similarity: {result['similarity']:.4f})")
        print(f"Source: {result['metadata'].get('source', 'Unknown')}")
        print(f"Page: {result['metadata'].get('page', 'Unknown')}")
        print(f"Content: {result['content'][:200]}...")
        print("-" * 60)
    
    return results.data


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
