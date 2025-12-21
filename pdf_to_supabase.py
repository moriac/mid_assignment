"""
PDF to Supabase Vector Store
Process PDF files, create embeddings, and store in Supabase
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


def load_pdf_files(folder_path: str) -> List:
    """Load all PDF files from the specified folder"""
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
    
    # Load all PDFs
    all_documents = []
    for pdf_file in pdf_files:
        print(f"\n📖 Loading: {pdf_file.name}")
        loader = PyPDFLoader(str(pdf_file))
        documents = loader.load()
        
        # Add source metadata
        for doc in documents:
            doc.metadata['source_file'] = pdf_file.name
        
        all_documents.extend(documents)
        print(f"  ✓ Loaded {len(documents)} pages")
    
    print(f"\n✅ Total pages loaded: {len(all_documents)}")
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
    print(f"\n🔮 Creating embeddings and storing in Supabase table '{table_name}'...")
    
    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create Supabase vector store
    vector_store = SupabaseVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        client=supabase_client,
        table_name=table_name,
        query_name=f"{table_name}_search"
    )
    
    print(f"✅ Successfully stored {len(chunks)} chunks in Supabase!")
    return vector_store


def main():
    """Main function to process PDFs and store in Supabase"""
    print("=" * 60)
    print("PDF to Supabase Vector Store")
    print("=" * 60)
    
    try:
        # Configuration
        pdf_folder = "tik"
        chunk_size = 200
        table_name = "small_chunks"
        
        # Step 1: Initialize Supabase
        print("\n🔌 Connecting to Supabase...")
        supabase_client = initialize_supabase()
        print("✅ Connected to Supabase")
        
        # Step 2: Load PDF files
        documents = load_pdf_files(pdf_folder)
        
        # Step 3: Chunk documents
        chunks = chunk_documents(documents, chunk_size=chunk_size)
        
        # Step 4: Create embeddings and store
        vector_store = create_embeddings_and_store(chunks, supabase_client, table_name)
        
        print("\n" + "=" * 60)
        print("✨ Process completed successfully!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"  - PDF files processed: {len(list(Path(pdf_folder).glob('*.pdf')))}")
        print(f"  - Total chunks created: {len(chunks)}")
        print(f"  - Chunk size: {chunk_size} characters")
        print(f"  - Table name: {table_name}")
        print(f"  - Embedding model: text-embedding-3-small")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
