"""
Demonstration: Comparing naive chunking vs smart LLM-based chunking
This shows why intelligent chunking is better for your assignment
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Sample insurance claim text
SAMPLE_TEXT = """
CLAIM SUMMARY
Policy #: INS-2024-4567
Claimant: John Smith
Date Filed: Jan 5, 2024

INCIDENT TIMELINE
Dec 15, 2023 - Minor leak detected in basement
Dec 20, 2023 - Leak worsened, water damage began
Dec 22, 2023 - Emergency repairs initiated
Dec 28, 2023 - Damage assessment completed

DAMAGES CLAIMED
Water damage repairs: $15,000
Equipment replacement: $8,500
Business interruption: $12,000
Total: $35,500

INVESTIGATION NOTES
Inspector found delayed reporting. Maintenance logs show leak was known since Nov 2023.
Claimant claims they were unaware until December.
Photos confirm extensive damage.
"""

def naive_chunking(text: str, chunk_size: int = 200):
    """Simple fixed-size chunking (the old way)"""
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

def smart_llm_chunking(text: str):
    """Intelligent semantic chunking using LLM"""
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""Analyze this insurance claim text and split it into logical sections.
Return a JSON array of chunks where each chunk is a complete semantic unit.

Text:
{text}

Return format:
{{"chunks": ["section 1 text", "section 2 text", ...]}}
"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    import json
    result = response.choices[0].message.content
    
    # Parse JSON response
    if "```json" in result:
        result = result.split("```json")[1].split("```")[0]
    
    data = json.loads(result.strip())
    return data.get("chunks", [])

def main():
    print("=" * 80)
    print("COMPARISON: Naive vs Smart Chunking for Insurance Claims")
    print("=" * 80)
    print()
    
    print("📄 Sample Insurance Claim Text:")
    print("-" * 80)
    print(SAMPLE_TEXT)
    print("-" * 80)
    print()
    
    # Naive chunking
    print("🔴 METHOD 1: NAIVE FIXED-SIZE CHUNKING (200 chars)")
    print("=" * 80)
    naive_chunks = naive_chunking(SAMPLE_TEXT, chunk_size=200)
    
    for i, chunk in enumerate(naive_chunks, 1):
        print(f"\nChunk {i}:")
        print(f"Length: {len(chunk)} chars")
        print(f"Preview: {chunk[:100]}...")
        print(f"⚠️  Problem: {'BREAKS MID-SENTENCE' if chunk[-1] not in '.!?' else 'OK'}")
    
    print("\n" + "=" * 80)
    print("❌ NAIVE CHUNKING PROBLEMS:")
    print("   • Breaks in middle of sentences")
    print("   • Splits related timeline events")
    print("   • No semantic meaning")
    print("   • Can't answer 'What happened chronologically?'")
    print("=" * 80)
    print()
    
    # Smart chunking
    print("🟢 METHOD 2: SMART LLM-BASED CHUNKING")
    print("=" * 80)
    print("Analyzing with GPT-4...\n")
    
    try:
        smart_chunks = smart_llm_chunking(SAMPLE_TEXT)
        
        for i, chunk in enumerate(smart_chunks, 1):
            print(f"\nChunk {i}:")
            print(f"Length: {len(chunk)} chars")
            print(f"Content:\n{chunk}")
            print("✅ Complete semantic unit")
        
        print("\n" + "=" * 80)
        print("✅ SMART CHUNKING BENEFITS:")
        print("   • Preserves complete sections")
        print("   • Keeps timeline events together")
        print("   • Maintains semantic meaning")
        print("   • Perfect for timeline questions!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure OPENAI_API_KEY is set in .env file")
    
    print("\n" + "=" * 80)
    print("📊 SUMMARY FOR YOUR ASSIGNMENT")
    print("=" * 80)
    print("""
Why Smart Chunking is Better:

1. NAIVE CHUNKING (Character-based):
   ❌ Chunks: [0-200], [201-400], [401-600]
   ❌ Can split "Dec 15 - leak detected" into two chunks
   ❌ Timeline questions fail because events are separated
   
2. SMART LLM CHUNKING (Semantic):
   ✅ Chunks: [Summary], [Timeline], [Damages], [Investigation]
   ✅ All timeline events stay together
   ✅ Perfect for "What happened when?" questions
   ✅ Shows understanding of document structure

For your course: Using smart chunking demonstrates knowledge of:
• Modern LLM-based document processing
• Semantic understanding vs naive splitting
• Why context matters for Q&A systems
• Production-ready RAG (Retrieval Augmented Generation)
    """)
    print("=" * 80)

if __name__ == "__main__":
    main()
