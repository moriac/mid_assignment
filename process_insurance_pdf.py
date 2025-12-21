"""
Process insurance_claim_case.pdf and store in Supabase
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from supabase.client import create_client

# For OCR
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from langchain_core.documents import Document

# Set Tesseract path explicitly
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load environment variables
load_dotenv()


def initialize_supabase():
    """Initialize Supabase client"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials in .env file")
    
    return create_client(supabase_url, supabase_key)


def extract_text_with_ocr(pdf_path: str):
    """Extract text from PDF using OCR"""
    print(f"📖 Loading: {Path(pdf_path).name}")
    
    doc = fitz.open(pdf_path)
    documents = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        
        # If no text found, use OCR
        if not text.strip():
            print(f"  Page {page_num + 1}: Using OCR...")
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img, lang='heb+eng')
        
        if text.strip():
            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        'source': Path(pdf_path).name,
                        'page': page_num + 1
                    }
                )
            )
            print(f"  ✓ Page {page_num + 1}: {len(text)} characters")
    
    doc.close()
    print(f"  ✅ Total: {len(documents)} pages\n")
    return documents


def main():
    print("=" * 60)
    print("Processing insurance_claim_case.pdf")
    print("=" * 60)
    
    # Configuration
    pdf_file = "insurance_claim_case.pdf"
    chunk_size = 200
    table_name = "small_chunks"
    
    # Step 1: Initialize Supabase
    print("\n🔌 Connecting to Supabase...")
    supabase_client = initialize_supabase()
    print("✅ Connected\n")
    
    # Step 2: Extract text from PDF
    documents = extract_text_with_ocr(pdf_file)
    
    if not documents:
        print("❌ No text extracted from PDF!")
        return
    
    # Step 3: Chunk documents
    print(f"✂️ Splitting into {chunk_size}-character chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=20,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} chunks\n")
    
    # Step 4: Create embeddings and store
    print(f"🔮 Creating embeddings and storing in '{table_name}'...")
    print(f"⏳ Processing {len(chunks)} chunks...\n")
    
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Process in batches
    inserted_count = 0
    batch_size = 20  # Smaller batches for better reliability
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"  Batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}...", end=" ")
        
        try:
            records = []
            for doc in batch:
                embedding_vector = embeddings.embed_query(doc.page_content)
                record = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "embedding": embedding_vector
                }
                records.append(record)
            
            supabase_client.table(table_name).insert(records).execute()
            inserted_count += len(records)
            print(f"✓ {inserted_count}/{len(chunks)}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print(f"  Skipping batch and continuing...")
            continue
    
    print(f"\n✅ Successfully stored {inserted_count} chunks!")
    
    print("\n" + "=" * 60)
    print("✨ Process completed!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  - File: {pdf_file}")
    print(f"  - Pages: {len(documents)}")
    print(f"  - Chunks: {len(chunks)}")
    print(f"  - Chunk size: {chunk_size} characters")
    print(f"  - Table: {table_name}")


if __name__ == "__main__":
    main()
