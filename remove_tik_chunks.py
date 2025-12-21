"""
Remove chunks from the 5 PDF files in the tik folder
"""

import os
from dotenv import load_dotenv
from supabase.client import create_client

load_dotenv()

def initialize_supabase():
    """Initialize Supabase client"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing Supabase credentials in .env file")
    
    return create_client(supabase_url, supabase_key)


def main():
    print("=" * 60)
    print("Removing chunks from tik folder PDFs")
    print("=" * 60)
    
    # The 5 PDF files from tik folder
    tik_pdfs = [
        "moked.pdf",
        "police.pdf",
        "tik_refui.pdf",
        "כתב_תביעה.pdf",
        "תצהיר_בריאות.pdf"
    ]
    
    print("\n🔌 Connecting to Supabase...")
    supabase_client = initialize_supabase()
    print("✅ Connected\n")
    
    table_name = "small_chunks"
    total_deleted = 0
    
    for pdf_file in tik_pdfs:
        print(f"🗑️  Removing chunks from: {pdf_file}...", end=" ")
        
        # Delete all chunks where metadata->>'source' matches this PDF
        result = supabase_client.table(table_name).delete().eq(
            "metadata->>source", pdf_file
        ).execute()
        
        deleted_count = len(result.data) if result.data else 0
        total_deleted += deleted_count
        print(f"✓ Deleted {deleted_count} chunks")
    
    print("\n" + "=" * 60)
    print("✨ Cleanup completed!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  - PDFs processed: {len(tik_pdfs)}")
    print(f"  - Total chunks deleted: {total_deleted}")
    print(f"  - Remaining: Only insurance_claim_case.pdf chunks (106)")


if __name__ == "__main__":
    main()
