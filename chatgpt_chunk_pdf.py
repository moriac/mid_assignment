"""
Use ChatGPT to intelligently chunk PDF by sub-chapters and store in Supabase
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from supabase.client import create_client
from langchain_openai import OpenAIEmbeddings

# For PDF reading
import fitz  # PyMuPDF

load_dotenv()


def initialize_supabase():
    """Initialize Supabase client"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials in .env file")
    
    return create_client(supabase_url, supabase_key)


def extract_pdf_text(pdf_path: str):
    """Extract all text from PDF"""
    print(f"📖 Extracting text from: {Path(pdf_path).name}")
    
    doc = fitz.open(pdf_path)
    full_text = ""
    page_count = len(doc)
    
    for page_num in range(page_count):
        page = doc[page_num]
        text = page.get_text()
        full_text += f"\n--- Page {page_num + 1} ---\n{text}"
    
    doc.close()
    print(f"✅ Extracted {len(full_text)} characters from {page_count} pages\n")
    return full_text


def chunk_with_chatgpt(pdf_text: str):
    """Use ChatGPT to intelligently chunk the PDF by meaningful sections"""
    print("🤖 Sending to ChatGPT for intelligent chunking...")
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = """You are analyzing an actual insurance claim case document. Your task is to EXTRACT and PRESERVE the actual content from this document, organizing it into logical sections.

CRITICAL: You must include the ACTUAL TEXT from the document, not generic descriptions. Preserve:
- Specific names, dates, policy numbers, and amounts
- Actual incident descriptions as written
- Real medical findings and diagnoses
- Concrete facts and details from the case

Organize the content into sections based on natural divisions in the document, such as:
- Case overview (with actual policy number, names, dates)
- Incident description (actual events as described)
- Medical records (specific diagnoses, treatments, dates)
- Claim details (actual amounts, calculations)
- Investigation findings (real evidence and statements)
- Decision and outcome (actual decision with amounts)

Return ONLY a valid JSON object with this exact format:
{
  "chunks": [
    {
      "title": "Brief descriptive title",
      "content": "THE ACTUAL EXTRACTED TEXT from this section, including all specific details, names, dates, amounts, and facts. This should be the real content from the PDF, not a generic description."
    }
  ]
}

RULES:
1. Extract actual text from the PDF, don't paraphrase or generalize
2. Include specific details: names, dates, amounts, policy numbers
3. Each chunk should be 300-1500 words of actual content
4. Preserve important verbatim quotes and specific language
5. Don't write "The document states..." - just include the actual content
6. Return ONLY the JSON object, no other text

Here is the insurance claim document to extract from:

"""
    
    response = client.chat.completions.create(
        model="gpt-4o",  # Use stronger model for better extraction
        messages=[
            {
                "role": "system",
                "content": "You are a document extraction expert. Extract actual content from documents, preserving specific details, facts, and figures. Never generate generic summaries. Always return valid JSON."
            },
            {
                "role": "user",
                "content": prompt + pdf_text
            }
        ],
        temperature=0.1  # Very low temperature for accurate extraction
    )
    
    result = response.choices[0].message.content
    print("✅ Received response from ChatGPT\n")
    
    # Parse and validate
    try:
        if "```json" in result:
            json_start = result.find("```json") + 7
            json_end = result.find("```", json_start)
            result = result[json_start:json_end].strip()
        elif "```" in result:
            json_start = result.find("```") + 3
            json_end = result.find("```", json_start)
            result = result[json_start:json_end].strip()
        
        chunks_data = json.loads(result)
        chunks_list = chunks_data.get("chunks", [])
        
        chunks = []
        for chunk_obj in chunks_list:
            if isinstance(chunk_obj, dict):
                title = chunk_obj.get("title", "Untitled Section")
                content = chunk_obj.get("content", "")
                
                # Validate content has specific details
                if len(content.strip()) < 200:
                    print(f"  ⚠️ Skipping short chunk: '{title}' ({len(content)} chars)")
                    continue
                
                # Check for actual content vs generic descriptions
                generic_phrases = [
                    "this section provides",
                    "the document describes",
                    "this chunk focuses on",
                    "typically includes",
                    "may include"
                ]
                
                is_generic = any(phrase in content.lower()[:200] for phrase in generic_phrases)
                if is_generic:
                    print(f"  ⚠️ Warning: '{title}' appears generic - ensure actual data extraction")
                
                full_chunk = f"Section: {title}\n\n{content}"
                chunks.append(full_chunk)
                print(f"  ✓ '{title}' ({len(content)} chars)")
            elif isinstance(chunk_obj, str):
                # Fallback if format is just strings
                if len(chunk_obj.strip()) >= 200:
                    chunks.append(chunk_obj)
                    print(f"  ✓ Text chunk ({len(chunk_obj)} chars)")
        
        if not chunks:
            print("❌ No valid chunks extracted!")
            return []
        
        print(f"\n📊 Successfully extracted {len(chunks)} sections with actual content\n")
        
        # Show first chunk preview to verify it has actual data
        if chunks:
            print("📋 First chunk preview:")
            print(chunks[0][:300])
            print("...\n")
        
        return chunks
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Response preview: {result[:500]}...")
        return []


def store_in_supabase(chunks: list, table_name: str = "summary_chunks"):
    """Store chunks in Supabase with embeddings"""
    print(f"\n🔮 Creating embeddings and storing in '{table_name}'...")
    
    supabase_client = initialize_supabase()
    
    # Clear existing data for this source to avoid duplicates
    print("  🗑️ Clearing existing chunks from this source...")
    try:
        supabase_client.table(table_name).delete().eq(
            "metadata->>source", "insurance_claim_case.pdf"
        ).execute()
        print("  ✓ Existing chunks cleared")
    except Exception as e:
        print(f"  ⚠️ Could not clear existing chunks: {e}")
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    inserted_count = 0
    
    for i, chunk_text in enumerate(chunks, 1):
        print(f"  Processing chunk {i}/{len(chunks)}...", end=" ")
        
        try:
            # Create embedding
            embedding_vector = embeddings.embed_query(chunk_text)
            
            # Extract title if present
            title = "Section"
            if chunk_text.startswith("Section:"):
                first_line_end = chunk_text.find("\n")
                if first_line_end > 0:
                    title = chunk_text[9:first_line_end].strip()
            
            # Prepare record
            record = {
                "content": chunk_text,
                "metadata": {
                    "source": "insurance_claim_case.pdf",
                    "chunk_number": i,
                    "chunk_type": "insurance_section",
                    "title": title,
                    "char_count": len(chunk_text)
                },
                "embedding": embedding_vector
            }
            
            # Insert into Supabase
            supabase_client.table(table_name).insert(record).execute()
            inserted_count += 1
            print("✓")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            continue
    
    print(f"\n✅ Successfully stored {inserted_count} chunks in '{table_name}'!")
    return inserted_count


def verify_chunks(table_name: str = "summary_chunks"):
    """Verify the quality of stored chunks"""
    print(f"\n🔍 Verifying chunks in '{table_name}'...")
    
    supabase_client = initialize_supabase()
    
    try:
        result = supabase_client.table(table_name).select(
            "id, content, metadata"
        ).eq("metadata->>source", "insurance_claim_case.pdf").execute()
        
        if not result.data:
            print("  ❌ No chunks found!")
            return False
        
        print(f"  ✓ Found {len(result.data)} chunks")
        print("\n  Sample chunks:")
        
        for i, chunk in enumerate(result.data[:3], 1):
            content = chunk['content']
            title = chunk.get('metadata', {}).get('title', 'Unknown')
            preview = content[:200].replace('\n', ' ')
            print(f"\n  Chunk {i} - {title}:")
            print(f"    {preview}...")
            print(f"    (Length: {len(content)} chars)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Verification error: {e}")
        return False


def main():
    print("=" * 60)
    print("ChatGPT-Powered PDF Chunking for Insurance Claims")
    print("=" * 60)
    
    pdf_file = "insurance_claim_case.pdf"
    
    # Verify PDF exists
    if not os.path.exists(pdf_file):
        print(f"❌ PDF file not found: {pdf_file}")
        return
    
    try:
        # Step 1: Extract PDF text
        pdf_text = extract_pdf_text(pdf_file)
        
        if len(pdf_text) < 500:
            print("⚠️ PDF text seems too short, check extraction")
            return
        
        # Step 2: Use ChatGPT to chunk intelligently
        chunks = chunk_with_chatgpt(pdf_text)
        
        if not chunks:
            print("❌ No valid chunks created by ChatGPT!")
            return
        
        # Step 3: Store in Supabase
        stored_count = store_in_supabase(chunks, "summary_chunks")
        
        if stored_count == 0:
            print("❌ No chunks were stored!")
            return
        
        # Step 4: Verify the chunks
        verify_chunks("summary_chunks")
        
        print("\n" + "=" * 60)
        print("✨ Process completed!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"  - File: {pdf_file}")
        print(f"  - Chunks created: {len(chunks)}")
        print(f"  - Chunks stored: {stored_count}")
        print(f"  - Table: summary_chunks")
        print(f"  - Embedding model: text-embedding-3-small")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
