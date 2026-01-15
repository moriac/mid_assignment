"""
Test summary_chunks retrieval specifically
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from langchain_openai import OpenAIEmbeddings

load_dotenv()

def test_summary_chunks_search():
    print("=" * 60)
    print("Testing summary_chunks Retrieval")
    print("=" * 60)
    
    # Initialize Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials")
        return
    
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Supabase connected\n")
    
    # Test 1: Direct table query
    print("Test 1: Direct table query")
    print("-" * 60)
    try:
        response = supabase.table('summary_chunks').select('*').limit(3).execute()
        print(f"✅ Retrieved {len(response.data)} rows directly")
        for i, row in enumerate(response.data, 1):
            print(f"\n  Row {i}:")
            print(f"    ID: {row['id']}")
            print(f"    Content: {row['content'][:100]}...")
            print(f"    Metadata: {row['metadata']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Vector similarity search using RPC
    print("\n\nTest 2: Vector similarity search")
    print("-" * 60)
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        query_embedding = embeddings.embed_query("insurance claim summary")
        print(f"✅ Generated embedding (dimension: {len(query_embedding)})")
        
        # Call the RPC function
        results = supabase.rpc(
            'summary_chunks_search',
            {
                'query_embedding': query_embedding,
                'match_count': 3
            }
        ).execute()
        
        if results.data:
            print(f"✅ Found {len(results.data)} similar chunks\n")
            for i, chunk in enumerate(results.data, 1):
                print(f"  Chunk {i}:")
                print(f"    ID: {chunk['id']}")
                print(f"    Similarity: {chunk['similarity']:.4f}")
                print(f"    Content: {chunk['content'][:150]}...")
                print(f"    Metadata: {chunk['metadata']}")
                print()
        else:
            print("⚠️ RPC function returned no results")
            print("This could mean:")
            print("  - The function exists but returned no matches")
            print("  - The embeddings might be NULL in the database")
            
    except Exception as e:
        print(f"❌ RPC Error: {e}")
        print("\nPossible issues:")
        print("  1. The 'summary_chunks_search' function doesn't exist in Supabase")
        print("  2. The function signature doesn't match")
        print("  3. RLS (Row Level Security) is blocking the function call")
        print("\nTo fix:")
        print("  - Run setup_summary_chunks_table.sql in Supabase SQL Editor")
        print("  - Check that the function was created successfully")
        print("  - Disable RLS on summary_chunks table or create appropriate policies")

if __name__ == "__main__":
    test_summary_chunks_search()
