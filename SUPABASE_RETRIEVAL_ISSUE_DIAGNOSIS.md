# Supabase Retrieval Issue - Diagnosis and Solutions

## 🔍 Issue Summary

**Problem:** No relevant chunks are being returned from Supabase when executing the test, despite having data in the table.

**Root Cause:** Embeddings are stored as **STRING** type instead of **VECTOR** type in PostgreSQL.

---

## 📊 Diagnostic Results

### 1. Table Status
- ✅ Table `summary_chunks` exists
- ✅ Table contains 6 rows of data
- ✅ Content and metadata are properly stored
- ❌ Embeddings are stored as **STRING** instead of **VECTOR(1536)**

### 2. Embedding Format Issue
```
Expected: VECTOR(1536) - PostgreSQL vector type
Actual:   TEXT/STRING   - String representation of the array
```

When retrieved from database:
- Type: `<class 'str'>`
- Length: ~19,267 characters
- Format: `"[-0.0010035423,0.05099446,-0.0068740635,...]"`

### 3. RPC Function Behavior
- ✅ Function `summary_chunks_search` exists
- ✅ Function executes without error
- ❌ Returns 0 results because vector operations fail on string data

---

## 🔧 Why This Happens

### Possible Causes:

1. **Missing pgvector Extension**
   - The `pgvector` extension might not be enabled in Supabase
   - Without it, PostgreSQL treats VECTOR columns as TEXT

2. **Table Created Without Proper Type**
   - The table might have been created before running the SQL setup script
   - Column type might be TEXT/JSONB instead of VECTOR(1536)

3. **Data Inserted Incorrectly**
   - Embeddings were inserted as serialized strings instead of vector arrays
   - The insertion method didn't properly cast the data

---

## ✅ Solutions

### Solution 1: Check and Enable pgvector Extension

1. Go to Supabase Dashboard → SQL Editor
2. Run this command:
```sql
-- Check if pgvector is enabled
SELECT * FROM pg_extension WHERE extname = 'vector';

-- If not enabled, enable it
CREATE EXTENSION IF NOT EXISTS vector;
```

### Solution 2: Verify Table Schema

Check the actual column type:
```sql
SELECT column_name, data_type, udt_name 
FROM information_schema.columns 
WHERE table_name = 'summary_chunks' 
AND column_name = 'embedding';
```

**Expected result:**
- `data_type`: USER-DEFINED
- `udt_name`: vector

**If incorrect, recreate the table:**
```sql
-- Backup existing data first!
CREATE TABLE summary_chunks_backup AS 
SELECT * FROM summary_chunks;

-- Drop and recreate
DROP TABLE summary_chunks;

-- Run the complete setup script
-- (see setup_summary_chunks_table.sql)
```

### Solution 3: Re-populate Data with Correct Format

The data needs to be re-inserted with embeddings as proper vector arrays:

```python
# Example of correct insertion
from supabase import create_client
from langchain_openai import OpenAIEmbeddings

supabase = create_client(url, key)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Generate embedding as a list
embedding_vector = embeddings.embed_query("some text")

# Insert with proper format
supabase.table('summary_chunks').insert({
    'content': 'some content',
    'metadata': {'key': 'value'},
    'embedding': embedding_vector  # Pass as list, not string
}).execute()
```

### Solution 4: Update Existing Rows

If you want to keep existing data and just fix embeddings:

```python
"""
Script to regenerate and update embeddings in correct format
"""
from supabase import create_client
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

def fix_embeddings():
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_SERVICE_KEY")
    )
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Get all rows
    response = supabase.table('summary_chunks').select('*').execute()
    
    for row in response.data:
        # Regenerate embedding from content
        new_embedding = embeddings.embed_query(row['content'])
        
        # Update the row
        supabase.table('summary_chunks').update({
            'embedding': new_embedding
        }).eq('id', row['id']).execute()
        
        print(f"Updated row {row['id']}")

if __name__ == "__main__":
    fix_embeddings()
```

---

## 🎯 Recommended Quick Fix

**Option A: Fresh Start (Recommended if you have few rows)**

1. Drop the existing table
2. Run `setup_summary_chunks_table.sql` in Supabase SQL Editor
3. Re-run your population script (e.g., `populate_supabase_hierarchical.py`)

**Option B: Keep Data (If you have important data)**

1. Verify pgvector is enabled
2. Check if column type is correct
3. Update existing embeddings using the script in Solution 4

---

## 🔬 Testing the Fix

After applying the fix, run this test:

```python
python test_summary_chunks_retrieval.py
```

**Expected output:**
```
Test 2: Vector similarity search
------------------------------------------------------------
✅ Generated embedding (dimension: 1536)
✅ Found 3 similar chunks

  Chunk 1:
    ID: 22
    Similarity: 0.8542
    Content: Section: Case Overview...
```

---

## 📝 Prevention

To avoid this issue in the future:

1. **Always enable pgvector first:**
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Create tables with proper schema:**
   ```sql
   CREATE TABLE summary_chunks (
       id BIGSERIAL PRIMARY KEY,
       content TEXT NOT NULL,
       metadata JSONB,
       embedding VECTOR(1536)  -- Not TEXT or JSONB!
   );
   ```

3. **Verify insertion:**
   After inserting data, check the type:
   ```python
   result = supabase.table('summary_chunks').select('embedding').limit(1).execute()
   print(type(result.data[0]['embedding']))  # Should be <class 'list'>
   ```

4. **Test immediately:**
   Always test vector search right after populating data

---

## 📚 Related Files

- `setup_summary_chunks_table.sql` - Table creation script
- `populate_supabase_hierarchical.py` - Data population script
- `test_summary_chunks_retrieval.py` - Test script
- `debug_vector_search.py` - Diagnostic script
- `check_embeddings_status.py` - Embedding verification script

---

## 🆘 Still Having Issues?

If the problem persists after trying these solutions:

1. Check Supabase logs in the Dashboard
2. Verify your Supabase project has the latest pgvector version
3. Check if RLS (Row Level Security) policies are interfering
4. Try a simple test with just one row to isolate the issue

---

**Last Updated:** January 14, 2026
**Status:** Issue Identified - Solutions Provided
