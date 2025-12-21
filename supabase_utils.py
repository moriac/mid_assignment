import os
from dotenv import load_dotenv
from supabase.client import create_client
from langchain_openai import OpenAIEmbeddings

load_dotenv()

def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise ValueError("Missing Supabase credentials in .env file")
    return create_client(url, key)

def get_top_k_chunks_from_small_chunks(query, k=3):
    """Retrieve top k relevant chunks from small_chunks table using embedding search."""
    client = get_supabase_client()
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    query_embedding = embeddings.embed_query(query)
    # Call the similarity search function
    results = client.rpc(
        "small_chunks_search",
        {
            "query_embedding": query_embedding,
            "match_count": k
        }
    ).execute()
    if not results.data:
        return []
    return [r["content"] for r in results.data]
