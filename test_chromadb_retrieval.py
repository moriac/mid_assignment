"""
Test ChromaDB retrieval with intelligent Q&A on insurance claims
"""

import os
from dotenv import load_dotenv
import chromadb
from openai import OpenAI

load_dotenv()


def initialize_chromadb():
    """Initialize ChromaDB client"""
    print("🔧 Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="insurance_claims")
    print(f"✅ Connected: {collection.count()} documents in collection\n")
    return collection


def query_chromadb(collection, question: str, n_results: int = 5):
    """Query ChromaDB for relevant chunks"""
    print(f"🔍 Searching for: '{question}'")
    
    results = collection.query(
        query_texts=[question],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    if not results['documents'][0]:
        print("  ❌ No results found!\n")
        return []
    
    print(f"  ✓ Found {len(results['documents'][0])} relevant chunks\n")
    
    # Format results
    chunks = []
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        chunks.append({
            'content': doc,
            'metadata': metadata,
            'distance': distance,
            'relevance_score': 1 - distance  # Convert distance to similarity
        })
        print(f"  Chunk {i+1}: {metadata.get('title', 'Unknown')} (score: {1-distance:.3f})")
    
    print()
    return chunks


def answer_question_with_llm(question: str, context_chunks: list):
    """Use OpenAI to answer question based on retrieved context"""
    print("🤖 Generating answer with ChatGPT...\n")
    
    # Build context from chunks
    context = "\n\n---\n\n".join([
        f"Section {i+1}: {chunk['metadata'].get('title', 'Unknown')}\n{chunk['content']}"
        for i, chunk in enumerate(context_chunks)
    ])
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""You are an expert at analyzing insurance claim documents. 
Answer the following question based ONLY on the provided context from the insurance claim case.

If the information is not in the context, say so. Be specific and cite relevant details like dates, names, and amounts when available.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an insurance claim analyst. Provide accurate, specific answers based on the given context. Include relevant dates, names, and amounts."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content


def test_question(collection, question: str):
    """Test a single question end-to-end"""
    print("=" * 70)
    print(f"❓ QUESTION: {question}")
    print("=" * 70)
    print()
    
    # Step 1: Retrieve relevant chunks
    chunks = query_chromadb(collection, question, n_results=5)
    
    if not chunks:
        print("❌ Cannot answer - no relevant information found.\n")
        return
    
    # Step 2: Generate answer
    answer = answer_question_with_llm(question, chunks)
    
    # Display results
    print("=" * 70)
    print("📋 ANSWER:")
    print("=" * 70)
    print(answer)
    print("=" * 70)
    print()
    
    # Show sources
    print("📚 Sources used:")
    for i, chunk in enumerate(chunks[:3], 1):
        title = chunk['metadata'].get('title', 'Unknown')
        score = chunk['relevance_score']
        print(f"  {i}. {title} (relevance: {score:.2%})")
    print()


def main():
    print("\n" + "=" * 70)
    print("🔬 ChromaDB Retrieval & Q&A Test")
    print("=" * 70)
    print()
    
    # Initialize ChromaDB
    collection = initialize_chromadb()
    
    # Check if we have data
    if collection.count() == 0:
        print("❌ No documents in ChromaDB!")
        print("💡 Run 'python chromadb_chunk_pdf.py' first to process your PDF.\n")
        return
    
    # Test questions focused on insurance claims and timelines
    test_questions = [
        "Give me a summary of the insurance claim case",
        "What are the key events in the timeline? List them chronologically.",
        "Who are the parties involved in this claim?",
        "What was the incident that led to this claim?",
        "What was the final outcome or decision of this claim?",
        "What were the medical findings or injuries reported?",
    ]
    
    print(f"Testing {len(test_questions)} questions...\n")
    
    for i, question in enumerate(test_questions, 1):
        test_question(collection, question)
        
        # Pause between questions (except last one)
        if i < len(test_questions):
            input("Press Enter to continue to next question...\n")
    
    print("=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)
    print()
    
    # Interactive mode
    print("💬 Interactive Q&A Mode (type 'quit' to exit)")
    print("-" * 70)
    while True:
        user_question = input("\nYour question: ").strip()
        if user_question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        if user_question:
            print()
            test_question(collection, user_question)


if __name__ == "__main__":
    main()
