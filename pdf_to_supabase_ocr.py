"""
PDF to Supabase Vector Store with OCR Support
Process scanned PDF files using OCR, create embeddings, and store in Supabase
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase.client import Client, create_client

# For OCR
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io

# Set Tesseract path explicitly
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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


def extract_text_with_ocr(pdf_path: str) -> List[dict]:
    """Extract text from PDF using OCR for scanned documents"""
    print(f"📖 Loading with OCR: {Path(pdf_path).name}")
    
    # Open PDF with PyMuPDF
    doc = fitz.open(pdf_path)
    documents = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # First, try to extract text directly
        text = page.get_text()
        
        # If no text found, use OCR
        if not text.strip():
            print(f"  Page {page_num + 1}: Using OCR...")
            # Convert page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Perform OCR (supports Hebrew with lang='heb+eng')
            text = pytesseract.image_to_string(img, lang='heb+eng')
        
        if text.strip():
            documents.append({
                'page_content': text,
                'metadata': {
                    'source': Path(pdf_path).name,
                    'page': page_num + 1
                }
            })
            print(f"  ✓ Page {page_num + 1}: {len(text)} characters")
        else:
            print(f"  ⚠️ Page {page_num + 1}: No text extracted")
    
    doc.close()
    return documents


def load_pdf_files_with_ocr(folder_path: str) -> List:
    """Load all PDF files from the specified folder using OCR"""
    pdf_folder = Path(folder_path)
    
    if not pdf_folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    # Get all PDF files
    pdf_files = list(pdf_folder.glob("*.pdf"))
    
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in: {folder_path}")
    
    print(f"📁 Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        print(f"  - {pdf.name}")
    print()
    
    # Load all PDFs with OCR
    all_documents = []
    for pdf_file in pdf_files:
        docs_data = extract_text_with_ocr(str(pdf_file))
        
        # Convert to LangChain Document format
        from langchain_core.documents import Document
        for doc_data in docs_data:
            doc = Document(
                page_content=doc_data['page_content'],
                metadata=doc_data['metadata']
            )
            all_documents.append(doc)
        
        print(f"  ✓ Total: {len(docs_data)} pages with text\n")
    
    print(f"✅ Total pages loaded: {len(all_documents)}")
    return all_documents


def chunk_documents(documents: List, chunk_size: int = 200, chunk_overlap: int = 20) -> List:
    """Split documents into chunks"""
    print(f"\n✂️ Splitting documents into chunks of size {chunk_size}...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} chunks")
    
    return chunks


def create_embeddings_and_store(chunks: List, supabase_client: Client, table_name: str = "small_chunks"):
    """Create embeddings and store in Supabase"""
    if not chunks:
        print("\n⚠️ No chunks to process. PDFs might be empty or OCR failed.")
        return None
    
    print(f"\n🔮 Creating embeddings and storing in Supabase table '{table_name}'...")
    print(f"⏳ Processing {len(chunks)} chunks (this may take a few minutes)...")
    
    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Manually insert chunks to avoid ID type issues
    inserted_count = 0
    batch_size = 50
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        print(f"  Processing batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}...")
        
        # Prepare batch data
        records = []
        for doc in batch:
            # Create embedding
            embedding_vector = embeddings.embed_query(doc.page_content)
            
            # Prepare record without ID (let database auto-generate)
            record = {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "embedding": embedding_vector
            }
            records.append(record)
        
        # Insert into Supabase
        result = supabase_client.table(table_name).insert(records).execute()
        inserted_count += len(records)
        print(f"  ✓ Inserted {inserted_count}/{len(chunks)} chunks")
    
    print(f"✅ Successfully stored {inserted_count} chunks in Supabase!")
    return True


def main():
    """Main function to process PDFs and store in Supabase"""
    print("=" * 60)
    print("PDF to Supabase Vector Store (with OCR)")
    print("=" * 60)
    
    try:
        # Configuration
        pdf_folder = "tik"
        chunk_size = 200
        table_name = "small_chunks"
        
        # Step 1: Initialize Supabase
        print("\n🔌 Connecting to Supabase...")
        supabase_client = initialize_supabase()
        print("✅ Connected to Supabase\n")
        
        # Step 2: Load PDF files with OCR
        documents = load_pdf_files_with_ocr(pdf_folder)
        
        if not documents:
            print("\n❌ No text could be extracted from PDFs!")
            return
        
        # Step 3: Chunk documents
        chunks = chunk_documents(documents, chunk_size=chunk_size)
        
        # Step 4: Create embeddings and store
        vector_store = create_embeddings_and_store(chunks, supabase_client, table_name)
        
        print("\n" + "=" * 60)
        print("✨ Process completed successfully!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"  - PDF files processed: {len(list(Path(pdf_folder).glob('*.pdf')))}")
        print(f"  - Pages with text: {len(documents)}")
        print(f"  - Total chunks created: {len(chunks)}")
        print(f"  - Chunk size: {chunk_size} characters")
        print(f"  - Table name: {table_name}")
        print(f"  - Embedding model: text-embedding-3-small")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
