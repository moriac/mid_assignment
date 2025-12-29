"""
Populate Supabase with Hierarchical Chunks

This script builds the hierarchical index and stores the leaf node embeddings
in your Supabase hierarchical_chunks table.

Requirements:
1. SUPABASE_DB_PASSWORD set in .env
2. SQL setup script already run in Supabase
"""

import os
from dotenv import load_dotenv
from hierarchical_retriever import get_claim_retriever

load_dotenv()


def check_requirements():
    """Check if all requirements are met."""
    print("Checking requirements...")
    
    # Check for database password
    db_password = os.getenv("SUPABASE_DB_PASSWORD")
    if not db_password:
        print("\n❌ SUPABASE_DB_PASSWORD not set in .env file")
        print("\nTo fix this:")
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to Settings → Database")
        print("3. Find your database password")
        print("4. Add to .env file:")
        print("   SUPABASE_DB_PASSWORD=your_password_here")
        print("\nAlternatively, if you just want to test without Supabase:")
        print("   python hierarchical_retriever.py")
        print("   (This uses in-memory storage)")
        return False
    
    print("✓ SUPABASE_DB_PASSWORD is set")
    
    # Check other credentials
    if not os.getenv("SUPABASE_URL"):
        print("❌ SUPABASE_URL not set")
        return False
    print("✓ SUPABASE_URL is set")
    
    if not os.getenv("SUPABASE_SERVICE_KEY"):
        print("❌ SUPABASE_SERVICE_KEY not set")
        return False
    print("✓ SUPABASE_SERVICE_KEY is set")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set")
        return False
    print("✓ OPENAI_API_KEY is set")
    
    # Check PDF exists
    if not os.path.exists("insurance_claim_case.pdf"):
        print("❌ insurance_claim_case.pdf not found")
        return False
    print("✓ insurance_claim_case.pdf found")
    
    print("\n✓ All requirements met!\n")
    return True


def populate_supabase():
    """Build hierarchical index and populate Supabase."""
    print("=" * 70)
    print("POPULATING SUPABASE WITH HIERARCHICAL CHUNKS")
    print("=" * 70)
    print()
    
    if not check_requirements():
        return False
    
    print("Building hierarchical index with Supabase vector store...")
    print("This will:")
    print("1. Parse the PDF into a hierarchy (2048/512/128 chars)")
    print("2. Generate embeddings for 44 leaf nodes")
    print("3. Store them in your Supabase hierarchical_chunks table")
    print()
    
    try:
        # Build with Supabase enabled
        retriever = get_claim_retriever(
            rebuild=True,  # Force rebuild
            use_supabase=True  # Enable Supabase storage
        )
        
        print("\n" + "=" * 70)
        print("✓ SUCCESS!")
        print("=" * 70)
        print("\nYour Supabase hierarchical_chunks table should now contain:")
        print("- 44 leaf node embeddings")
        print("- Each with 1536-dimensional vectors")
        print("- Ready for similarity search")
        print()
        print("You can now query your data:")
        print('  nodes = retriever.retrieve("claim date")')
        print()
        
        return True
        
    except ValueError as e:
        if "SUPABASE_DB_PASSWORD" in str(e):
            print("\n❌ Error: Database password issue")
            print(str(e))
            return False
        raise
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_storage():
    """Verify that data was stored in Supabase."""
    print("\n" + "=" * 70)
    print("VERIFYING SUPABASE STORAGE")
    print("=" * 70)
    
    try:
        from supabase_utils import get_supabase_client
        
        client = get_supabase_client()
        
        # Query the table
        result = client.table("hierarchical_chunks").select("id").execute()
        
        if result.data:
            count = len(result.data)
            print(f"\n✓ Found {count} records in hierarchical_chunks table")
            
            # Get a sample record
            sample = client.table("hierarchical_chunks").select("*").limit(1).execute()
            if sample.data:
                print("\nSample record:")
                record = sample.data[0]
                print(f"  ID: {record.get('id')}")
                print(f"  Node ID: {record.get('node_id', 'N/A')}")
                print(f"  Text length: {len(record.get('text', ''))} chars")
                print(f"  Has embedding: {bool(record.get('embedding'))}")
        else:
            print("\n⚠ Table is empty - data may not have been stored")
            print("\nPossible reasons:")
            print("1. The script didn't run successfully")
            print("2. Using in-memory storage instead of Supabase")
            print("3. Table name mismatch")
            
    except Exception as e:
        print(f"\n⚠ Could not verify: {e}")


if __name__ == "__main__":
    print("\n")
    success = populate_supabase()
    
    if success:
        verify_storage()
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print("\n1. Check your Supabase dashboard to see the data")
        print("2. Run queries:")
        print("   python quick_start_hierarchical.py")
        print("\n3. Or use in your code:")
        print("   from hierarchical_retriever import get_claim_retriever")
        print("   retriever = get_claim_retriever()")
        print("   nodes = retriever.retrieve('your query')")
        print()
    else:
        print("\n" + "=" * 70)
        print("TROUBLESHOOTING")
        print("=" * 70)
        print("\nIf you don't want to use Supabase storage:")
        print("- The in-memory version works fine for testing")
        print("- Run: python hierarchical_retriever.py")
        print("\nIf you want to use Supabase storage:")
        print("- Add SUPABASE_DB_PASSWORD to your .env file")
        print("- Run this script again")
        print()
