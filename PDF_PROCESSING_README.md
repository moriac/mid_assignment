# PDF to Supabase Vector Store

This script processes PDF files from the `tik` folder, breaks them into chunks, creates embeddings, and stores them in a Supabase vector database.

## 📋 Prerequisites

1. **Supabase Account**: Sign up at [supabase.com](https://supabase.com)
2. **OpenAI API Key**: Get one from [OpenAI](https://platform.openai.com/api-keys)

## 🚀 Setup Instructions

### Step 1: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 2: Configure Supabase

1. Create a new project in Supabase
2. Go to **Project Settings** → **API**
3. Copy your **Project URL** and **service_role key** (not the anon key!)
4. Update `.env` file with your credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key-here
```

### Step 3: Create Supabase Table

1. Go to your Supabase project
2. Navigate to **SQL Editor**
3. Run the SQL script from `setup_supabase_table.sql`

This will:
- Enable the `pgvector` extension
- Create the `small_chunks` table
- Set up similarity search function
- Create necessary indexes

### Step 4: Run the Script

```powershell
python pdf_to_supabase.py
```

## 📊 What It Does

1. **Loads PDFs**: Reads all PDF files from the `tik` folder
2. **Chunks Text**: Splits content into 200-character chunks with 20-character overlap
3. **Creates Embeddings**: Uses OpenAI's `text-embedding-3-small` model
4. **Stores in Supabase**: Saves embeddings to the `small_chunks` table

## 📁 PDF Files in `tik` Folder

- moked.pdf
- police.pdf
- tik_refui.pdf
- כתב_תביעה.pdf
- תצהיר_בריאות.pdf

## 🔍 Querying the Vector Store

After processing, you can query the vectors using similarity search:

```python
from supabase.client import create_client
from langchain_openai import OpenAIEmbeddings
import os

# Initialize
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Create query embedding
query = "your search query here"
query_embedding = embeddings.embed_query(query)

# Search
results = supabase.rpc(
    "small_chunks_search",
    {
        "query_embedding": query_embedding,
        "match_count": 5
    }
).execute()

print(results.data)
```

## ⚙️ Configuration

- **Chunk Size**: 200 characters (configurable in script)
- **Chunk Overlap**: 20 characters (configurable in script)
- **Embedding Model**: text-embedding-3-small (1536 dimensions)
- **Table Name**: small_chunks

## 🛠️ Troubleshooting

### Error: "Missing Supabase credentials"
- Make sure you've set `SUPABASE_URL` and `SUPABASE_SERVICE_KEY` in your `.env` file

### Error: "relation 'small_chunks' does not exist"
- Run the SQL script in `setup_supabase_table.sql` first

### Error: "extension 'vector' does not exist"
- The pgvector extension might not be enabled. Run the SQL script which includes the enable command

### PDF Loading Issues
- Ensure all PDF files in the `tik` folder are not corrupted
- Check that the PDFs are readable and not password-protected

## 📝 Notes

- The script uses `RecursiveCharacterTextSplitter` which intelligently splits on paragraphs, lines, and spaces
- Metadata includes the source filename for each chunk
- All 5 PDF files will be processed in a single run
