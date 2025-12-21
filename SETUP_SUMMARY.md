# PDF Processing and Vector Storage Setup - Summary

## ✅ What Has Been Created

### 1. Main Processing Script: `pdf_to_supabase.py`
- Loads all PDF files from the `tik` folder (5 PDFs found)
- Splits documents into chunks of **200 characters** with 20-character overlap
- Creates embeddings using OpenAI's `text-embedding-3-small` model
- Stores vectors in Supabase table named **`small_chunks`**

### 2. SQL Setup Script: `setup_supabase_table.sql`
- Creates the `small_chunks` table with pgvector support
- Sets up similarity search function
- Creates indexes for optimal performance

### 3. Query Script: `query_supabase.py`
- Interactive search tool to query the vector store
- Returns most relevant chunks based on similarity

### 4. Documentation: `PDF_PROCESSING_README.md`
- Complete setup instructions
- Troubleshooting guide
- Usage examples

### 5. Updated Files:
- **`requirements.txt`**: Added necessary dependencies
  - `langchain-community`
  - `pypdf`
  - `supabase`
  - `tiktoken`
- **`.env`**: Added Supabase configuration placeholders

## 📋 Next Steps to Run the Script

### Step 1: Configure Supabase
1. Go to [supabase.com](https://supabase.com) and create a new project
2. Navigate to **Project Settings** → **API**
3. Copy:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **service_role key** (NOT the anon key!)
4. Update your `.env` file:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_KEY=your-service-role-key-here
   ```

### Step 2: Create Database Table
1. In Supabase Dashboard, go to **SQL Editor**
2. Copy and paste the entire contents of `setup_supabase_table.sql`
3. Click **Run** to execute the SQL

### Step 3: Run the Processing Script
```powershell
C:/Dev/AI_Course/mid_assignment/.venv/Scripts/python.exe pdf_to_supabase.py
```

This will:
- Process all 5 PDFs in the `tik` folder
- Create approximately 200-character chunks
- Generate embeddings for each chunk
- Store everything in Supabase

### Step 4 (Optional): Query the Data
```powershell
C:/Dev/AI_Course/mid_assignment/.venv/Scripts/python.exe query_supabase.py
```

## 📊 Technical Details

- **Chunk Size**: 200 characters
- **Chunk Overlap**: 20 characters (to maintain context)
- **Embedding Model**: OpenAI text-embedding-3-small (1536 dimensions)
- **Vector Database**: Supabase with pgvector extension
- **Table Name**: `small_chunks`
- **PDF Files**: 5 files in the `tik` folder

## 🔧 Already Installed Packages

The following packages have been installed in your virtual environment:
- ✅ langchain-community
- ✅ pypdf
- ✅ supabase
- ✅ tiktoken

## ⚠️ Important Notes

1. **Service Key**: Make sure to use the `service_role` key from Supabase, NOT the `anon` key
2. **pgvector Extension**: The SQL script will enable it, but ensure your Supabase project supports it (all new projects do)
3. **OpenAI Costs**: Creating embeddings for all chunks will use your OpenAI API credits
4. **Processing Time**: Depending on PDF size, this may take a few minutes

## 📁 Files in the Project

```
mid_assignment/
├── tik/                           # Folder with PDF files
│   ├── moked.pdf
│   ├── police.pdf
│   ├── tik_refui.pdf
│   ├── כתב_תביעה.pdf
│   └── תצהיר_בריאות.pdf
├── pdf_to_supabase.py            # Main processing script
├── query_supabase.py             # Query/search script
├── setup_supabase_table.sql      # SQL setup script
├── PDF_PROCESSING_README.md      # Detailed documentation
├── requirements.txt              # Updated dependencies
└── .env                          # Configuration (add your keys!)
```

## 🎯 Ready to Use!

Everything is set up and ready. Just add your Supabase credentials to `.env` and run the script!
