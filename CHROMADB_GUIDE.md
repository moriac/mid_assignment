# ChromaDB Setup Guide for Insurance Claim Analysis

This guide shows you how to use **ChromaDB** with **intelligent LLM-based chunking** for your insurance claim PDF analysis assignment.

## 🎯 What You Get

- **Smart chunking**: Uses GPT-4 to intelligently split your PDF by meaningful sections
- **Simple storage**: ChromaDB runs locally, no server setup needed
- **Easy querying**: Ask questions about timelines, claims, and incidents
- **Vector search**: Automatically finds relevant sections using semantic similarity

## 📋 Quick Start

### 1. Setup Environment

Make sure you're in your virtual environment, then run:

```bash
# Activate virtual environment (if not already active)
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # Linux/Mac

# Run the setup script
python setup_chromadb_env.py
```

This will install all required dependencies:
- `chromadb` - Local vector database
- `openai` - For GPT-4 chunking and embeddings
- `python-dotenv` - Environment variables
- `pymupdf` - PDF text extraction

### 2. Configure API Keys

Create a `.env` file with your OpenAI API key:

```
OPENAI_API_KEY=sk-your-key-here
```

### 3. Process Your PDF

Run the chunking script to process `insurance_claim_case.pdf`:

```bash
python chromadb_chunk_pdf.py
```

**What this does:**
- Extracts all text from the PDF
- Sends it to GPT-4 for intelligent chunking
- Organizes content by sections (case overview, incident, claims, etc.)
- Stores chunks in ChromaDB with embeddings
- Creates a persistent database in `./chroma_db/`

### 4. Query and Test

Test the system with sample questions:

```bash
python test_chromadb_retrieval.py
```

This will:
- Ask 6 pre-defined questions about the claim
- Retrieve relevant chunks using vector search
- Generate answers using GPT-4
- Show sources for each answer
- Enter interactive mode for your own questions

## 🧠 How It Works

### Intelligent Chunking Process

1. **Extract**: Reads all text from PDF (preserves page numbers)
2. **Analyze**: GPT-4 identifies natural document sections:
   - Case Overview (policy info, dates, parties)
   - Incident Description (what happened, timeline)
   - Medical Records (diagnoses, treatments)
   - Claim Details (amounts, documentation)
   - Investigation Findings (evidence, statements)
   - Decision and Outcome (approval/denial, amounts)
3. **Chunk**: Creates semantic chunks (300-1500 words each)
4. **Embed**: Converts to vector embeddings
5. **Store**: Saves in ChromaDB for fast retrieval

### Retrieval and Q&A Process

1. **Question**: User asks about the claim
2. **Search**: ChromaDB finds top 5 most relevant chunks
3. **Context**: Chunks are combined as context
4. **Answer**: GPT-4 generates answer from context
5. **Citations**: Shows which sections were used

## 📊 Comparison: Traditional vs Smart Chunking

| Method | Traditional | Smart LLM Chunking |
|--------|------------|-------------------|
| **Split Logic** | Fixed size (e.g., 500 chars) | Semantic sections |
| **Context** | Often breaks mid-sentence | Preserves complete topics |
| **Timeline Questions** | May miss related events | Groups timeline together |
| **Accuracy** | Medium | High |
| **Setup** | Easy | Requires LLM API |
| **For Assignment** | ❌ Too simple | ✅ Impressive! |

## 🗂️ File Structure

```
mid_assignment/
├── chromadb_chunk_pdf.py          # Main chunking script
├── test_chromadb_retrieval.py     # Query and test script
├── setup_chromadb_env.py          # Dependency installer
├── insurance_claim_case.pdf       # Your PDF to analyze
├── .env                           # API keys (create this)
├── chroma_db/                     # Database (auto-created)
│   └── (ChromaDB files)
└── requirements.txt               # All dependencies
```

## 💡 Sample Questions You Can Ask

**Timeline Questions:**
- "What are the key events in the timeline?"
- "When did the incident occur?"
- "What happened chronologically?"

**Claim Details:**
- "What was claimed?"
- "What amounts were involved?"
- "What was the final outcome?"

**Parties Involved:**
- "Who are the parties in this claim?"
- "What was the claimant's name?"

**Investigation:**
- "What evidence was found?"
- "What were the investigation findings?"

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'chromadb'"

**Solution**: Make sure you're in your virtual environment
```bash
# Check if in venv (should show (.venv) in prompt)
# If not, activate it:
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install chromadb
pip install chromadb
```

### "PDF file not found"

**Solution**: Make sure `insurance_claim_case.pdf` is in the project root directory

### "No documents in ChromaDB"

**Solution**: Run the chunking script first:
```bash
python chromadb_chunk_pdf.py
```

### API Rate Limits

**Solution**: The script uses GPT-4 which can be rate-limited. If you hit limits:
- Wait a few minutes between runs
- Or change to `gpt-4o-mini` in the code (line 60 in chromadb_chunk_pdf.py)

## 🎓 For Your Assignment

### Why This Approach is Great for Assignments:

1. **Shows Understanding**: Demonstrates you know about semantic chunking vs naive splitting
2. **Modern Tech**: Uses cutting-edge LLM + vector DB approach
3. **Timeline-Aware**: Specifically handles timeline questions well
4. **Easy to Demo**: Simple setup, impressive results
5. **Local First**: No cloud dependencies (ChromaDB runs locally)

### What to Highlight:

- "I used GPT-4 to intelligently chunk the document by semantic sections"
- "ChromaDB provides local vector search without server setup"
- "The system preserves context for timeline-based questions"
- "Chunks are created based on meaning, not arbitrary character counts"

## 📚 Additional Resources

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [Vector Databases Explained](https://www.pinecone.io/learn/vector-database/)

## 🚀 Next Steps

1. ✅ Run `setup_chromadb_env.py` to install dependencies
2. ✅ Add your OpenAI API key to `.env`
3. ✅ Run `chromadb_chunk_pdf.py` to process your PDF
4. ✅ Run `test_chromadb_retrieval.py` to test queries
5. 🎯 Ask your own questions in interactive mode!

---

**Good luck with your AI course assignment! 🎓**
