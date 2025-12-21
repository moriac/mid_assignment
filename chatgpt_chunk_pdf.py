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
    """Use ChatGPT to intelligently chunk the PDF by sub-chapters"""
    print("🤖 Sending to ChatGPT for intelligent chunking...")
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = """You're an AI expert. Break the attached PDF content into chunks so that each chunk represents a sub-chapter in the PDF. 

Each chunk should be a meaningful, self-contained section of the document.

Return the answer ONLY as a valid JSON object with this exact format:
{
  "chunks": [
    "chunk 1 text here...",
    "chunk 2 text here...",
    ...
  ]
}

Do not include any other text outside the JSON object.

Here is the PDF content:

"""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are an expert at analyzing documents and breaking them into logical sub-chapters. Always return ONLY valid JSON, nothing else."
            },
            {
                "role": "user",
                "content": prompt + pdf_text
            }
        ],
        temperature=0.3
    )
    
    result = response.choices[0].message.content
    print("✅ Received response from ChatGPT\n")
    
    # Parse the JSON response
    try:
        chunks_data = json.loads(result)
        chunks = chunks_data.get("chunks", [])
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON parsing error, attempting to extract JSON from response...")
        # Try to extract JSON from markdown code blocks
        if "```json" in result:
            json_start = result.find("```json") + 7
            json_end = result.find("```", json_start)
            result = result[json_start:json_end].strip()
        elif "```" in result:
            json_start = result.find("```") + 3
            json_end = result.find("```", json_start)
            result = result[json_start:json_end].strip()
        
        chunks_data = json.loads(result)
        chunks = chunks_data.get("chunks", [])
    
    print(f"📊 ChatGPT created {len(chunks)} sub-chapter chunks\n")
    
    # Display chunk preview
    for i, chunk in enumerate(chunks, 1):
        preview = chunk[:100].replace('\n', ' ')
        print(f"  Chunk {i}: {preview}...")
    
    return chunks


def store_in_supabase(chunks: list, table_name: str = "summary_chunks"):
    """Store chunks in Supabase with embeddings"""
    print(f"\n🔮 Creating embeddings and storing in '{table_name}'...")
    
    supabase_client = initialize_supabase()
    
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
            
            # Prepare record
            record = {
                "content": chunk_text,
                "metadata": {
                    "source": "insurance_claim_case.pdf",
                    "chunk_number": i,
                    "chunk_type": "sub-chapter"
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


def main():
    print("=" * 60)
    print("ChatGPT-Powered PDF Chunking")
    print("=" * 60)
    
    pdf_file = "insurance_claim_case.pdf"
    
    try:
        # Step 1: Extract PDF text
        pdf_text = extract_pdf_text(pdf_file)
        
        # Step 2: Use ChatGPT to chunk by sub-chapters
        chunks = chunk_with_chatgpt(pdf_text)
        
        if not chunks:
            print("❌ No chunks created by ChatGPT!")
            return
        
        # Step 3: Store in Supabase
        stored_count = store_in_supabase(chunks, "summary_chunks")
        
        print("\n" + "=" * 60)
        print("✨ Process completed!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"  - File: {pdf_file}")
        print(f"  - Sub-chapter chunks: {len(chunks)}")
        print(f"  - Stored in: summary_chunks table")
        print(f"  - Embedding model: text-embedding-3-small")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
