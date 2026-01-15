"""
Fix embeddings in summary_chunks table - convert from STRING to proper VECTOR type
This script uses direct PostgreSQL connection to properly cast embeddings
"""

import os
import json
from dotenv import load_dotenv
import psycopg2

load_dotenv()


def get_postgres_connection():
    """Get a direct PostgreSQL connection"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_password = os.getenv("SUPABASE_DB_PASSWORD")
    
    if not supabase_url:
        raise ValueError("SUPABASE_URL not found in .env")
    
    if not supabase_password:
        raise ValueError(
            "SUPABASE_DB_PASSWORD not found in .env file.\n"
            "Please add it to your .env file:\n"
            "SUPABASE_DB_PASSWORD=your_database_password"
        )
    
    # Extract project reference from Supabase URL
    project_ref = supabase_url.replace("https://", "").replace(".supabase.co", "")
    
    # Construct database connection
    db_host = f"db.{project_ref}.supabase.co"
    
    print(f"Connecting to: {db_host}")
    
    conn = psycopg2.connect(
        host=db_host,
        port=5432,
        database="postgres",
        user="postgres",
        password=supabase_password
    )
    
    return conn


def fix_embeddings():
    """
    Fix the embedding column by converting string representations to proper VECTOR type
    """
    print("=" * 60)
    print("Fixing Embeddings in summary_chunks Table")
    print("=" * 60)
    
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        print("\n✅ Connected to database\n")
        
        # Get all rows that have embedding stored as text
        print("Fetching rows with embeddings...")
        cursor.execute("SELECT id, embedding::text FROM summary_chunks WHERE embedding IS NOT NULL")
        rows = cursor.fetchall()
        
        print(f"Found {len(rows)} rows with embeddings\n")
        
        fixed_count = 0
        
        for row_id, embedding_text in rows:
            try:
                # The embedding is already a string representation like "[0.1, 0.2, ...]"
                # We just need to update it with proper VECTOR casting
                
                # Verify it's valid JSON array
                embedding_list = json.loads(embedding_text)
                
                if not isinstance(embedding_list, list):
                    print(f"⚠️  Row {row_id}: Embedding is not a list, skipping")
                    continue
                
                print(f"Fixing row {row_id} (dimensions: {len(embedding_list)})...", end=" ")
                
                # Update the row with proper vector casting
                # We use the text representation and cast it to vector
                sql = """
                UPDATE summary_chunks
                SET embedding = %s::vector
                WHERE id = %s
                """
                
                cursor.execute(sql, (embedding_text, row_id))
                fixed_count += 1
                print("✅")
                
            except json.JSONDecodeError as e:
                print(f"❌ Row {row_id}: Invalid JSON - {e}")
                continue
            except Exception as e:
                print(f"❌ Row {row_id}: Error - {e}")
                continue
        
        # Commit all changes
        conn.commit()
        print(f"\n{'=' * 60}")
        print(f"✅ Successfully fixed {fixed_count}/{len(rows)} embeddings!")
        print(f"{'=' * 60}")
        
        # Verify the fix worked
        print("\nVerifying fix...")
        cursor.execute("""
            SELECT id, embedding <-> '[0,0,0,0,0]'::vector as distance 
            FROM summary_chunks 
            WHERE embedding IS NOT NULL 
            LIMIT 1
        """)
        
        test_result = cursor.fetchone()
        if test_result:
            print(f"✅ Vector operations are working! (test distance: {test_result[1]:.4f})")
        
        cursor.close()
        conn.close()
        
        print("\n✨ Embeddings are now properly stored as VECTOR type!")
        print("You can now run test_summary_chunks_retrieval.py again.\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Error type: {type(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()


if __name__ == "__main__":
    fix_embeddings()
