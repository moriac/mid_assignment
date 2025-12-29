# Hierarchical Auto-Merging Retriever - Quick Reference

## 🚀 One-Line Usage

```python
from hierarchical_retriever import get_claim_retriever
retriever = get_claim_retriever()
nodes = retriever.retrieve("your query here")
```

## 📦 Setup Checklist

- [ ] Install: `pip install -r requirements.txt`
- [ ] Add to `.env`: `SUPABASE_DB_PASSWORD=your_password`
- [ ] Run SQL: `setup_hierarchical_chunks_table.sql` in Supabase
- [ ] Test: `python test_hierarchical_retriever.py`
- [ ] Demo: `python hierarchical_retriever.py`

## 🔑 Key Functions

### Get Retriever
```python
from hierarchical_retriever import get_claim_retriever

# Basic
retriever = get_claim_retriever()

# Force rebuild
retriever = get_claim_retriever(rebuild=True)

# Custom PDF
retriever = get_claim_retriever(pdf_path="other.pdf")
```

### Retrieve Nodes
```python
# Basic retrieval
nodes = retriever.retrieve("claim date")

# With custom top-k
nodes = retriever.retrieve("claim date", similarity_top_k=10)

# Access node data
for node in nodes:
    print(f"Score: {node.score}")
    print(f"Text: {node.text}")
    print(f"ID: {node.node_id}")
```

### Query Engine (Q&A)
```python
from llama_index.core.query_engine import RetrieverQueryEngine

retriever = get_claim_retriever()
query_engine = RetrieverQueryEngine.from_args(retriever)

response = query_engine.query("What is the claim amount?")
print(response)
```

## 🏗️ Architecture at a Glance

```
PDF → HierarchicalParser → Nodes (2048/512/128)
                              ↓
                    ┌─────────┴─────────┐
                    ↓                   ↓
            All Nodes (Docstore)    Leaf Nodes (Vector Store)
                    ↓                   ↓
                    └─────────┬─────────┘
                              ↓
                    AutoMergingRetriever
                              ↓
                      Smart Retrieval
```

## 📊 What Gets Stored Where

| Component | Stores | Purpose |
|-----------|--------|---------|
| **SimpleDocumentStore** | ALL nodes (parents + leaves) | Auto-merging |
| **SupabaseVectorStore** | ONLY leaf nodes (128 chars) | Similarity search |
| **Result** | Merged parent nodes when applicable | Better context |

## 🎯 How Auto-Merging Works

1. Retrieve 6 leaf nodes (128 chars each)
2. Detect: 4 nodes have same parent
3. Merge: Combine into 1 parent (512 chars)
4. Return: 3 nodes with more context

**Before:** [128][128][128][128][128][128]  
**After:** [512 merged][128][128]  
**Result:** More context, same relevance!

## ⚙️ Configuration Options

### Chunk Sizes
```python
from hierarchical_retriever import HierarchicalClaimRetriever

# Default: [2048, 512, 128]
retriever = HierarchicalClaimRetriever(chunk_sizes=[2048, 512, 128])

# More context: larger chunks
retriever = HierarchicalClaimRetriever(chunk_sizes=[4096, 1024, 256])

# More precision: smaller chunks
retriever = HierarchicalClaimRetriever(chunk_sizes=[1024, 256, 64])
```

### Retrieval Parameters
```python
# Number of leaf nodes to retrieve
retriever.retrieve(query, similarity_top_k=6)  # default
retriever.retrieve(query, similarity_top_k=3)  # fewer
retriever.retrieve(query, similarity_top_k=10) # more
```

## 🔧 Common Tasks

### Task 1: Get Specific Information
```python
retriever = get_claim_retriever()
nodes = retriever.retrieve("policy number")
print(nodes[0].text)  # Most relevant chunk
```

### Task 2: Answer Questions
```python
from llama_index.core.query_engine import RetrieverQueryEngine

retriever = get_claim_retriever()
engine = RetrieverQueryEngine.from_args(retriever)
answer = engine.query("When was the claim filed?")
print(answer)
```

### Task 3: Get Context for Agent
```python
retriever = get_claim_retriever()
nodes = retriever.retrieve("incident details")
context = "\n\n".join([n.text for n in nodes])
# Use context in your agent prompt
```

### Task 4: Compare Retrievals
```python
# Get both hierarchical and simple results
from supabase_utils import get_top_k_chunks_from_small_chunks

query = "claim date"

# Hierarchical
h_nodes = get_claim_retriever().retrieve(query)
print(f"Hierarchical: {len(h_nodes)} nodes")

# Simple (if available)
s_chunks = get_top_k_chunks_from_small_chunks(query)
print(f"Simple: {len(s_chunks)} chunks")
```

## 📁 File Reference

| File | Purpose |
|------|---------|
| `hierarchical_retriever.py` | Main implementation |
| `setup_hierarchical_chunks_table.sql` | Database setup |
| `HIERARCHICAL_RETRIEVER_GUIDE.md` | Full documentation |
| `test_hierarchical_retriever.py` | Test suite |
| `quick_start_hierarchical.py` | Simple example |
| `integration_examples_hierarchical.py` | Integration patterns |

## 🐛 Troubleshooting

| Error | Solution |
|-------|----------|
| `Import "llama_index" could not be resolved` | `pip install -r requirements.txt` |
| `Missing Supabase credentials` | Add to `.env`: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` |
| `Missing SUPABASE_DB_PASSWORD` | Add to `.env` (find in Supabase dashboard) |
| `PDF file not found` | Ensure `insurance_claim_case.pdf` exists |
| `relation "hierarchical_chunks" does not exist` | Run SQL setup script |

## 📝 Environment Variables

```env
# Required
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...

# Required for hierarchical retriever
SUPABASE_DB_PASSWORD=your_db_password
```

## 🎓 Best Practices

1. **Cache the retriever** - Use `get_claim_retriever()` without `rebuild=True`
2. **Adjust top-k** - Start with 6, increase for more context
3. **Disable verbose** - Set `verbose=False` in production
4. **Monitor memory** - Docstore keeps all nodes in memory
5. **Rebuild sparingly** - Only when PDF changes

## 📊 Performance

| Metric | Value |
|--------|-------|
| First build | ~30-60 seconds |
| Cached retrieval | < 1 second |
| Retrieval latency | ~2-3 seconds |
| Memory usage | ~50-100 MB |

## 🔗 Integration Patterns

### Pattern 1: Direct Retrieval
```python
retriever = get_claim_retriever()
nodes = retriever.retrieve(query)
```

### Pattern 2: Query Engine
```python
engine = RetrieverQueryEngine.from_args(get_claim_retriever())
response = engine.query(query)
```

### Pattern 3: Agent Integration
```python
def my_agent(query):
    nodes = get_claim_retriever().retrieve(query)
    context = "\n".join([n.text for n in nodes])
    # Use context in LLM prompt
```

### Pattern 4: Hybrid Retrieval
```python
# Combine with existing retrieval
h_nodes = get_claim_retriever().retrieve(query)
s_chunks = get_top_k_chunks_from_small_chunks(query)
# Merge results
```

## 🎯 Quick Tests

```bash
# Test imports
python -c "from hierarchical_retriever import get_claim_retriever; print('OK')"

# Run full tests
python test_hierarchical_retriever.py

# Run demo
python hierarchical_retriever.py

# Quick start
python quick_start_hierarchical.py
```

## 📚 Learn More

- Full Guide: `HIERARCHICAL_RETRIEVER_GUIDE.md`
- Examples: `integration_examples_hierarchical.py`
- LlamaIndex Docs: https://developers.llamaindex.ai/
- AutoMergingRetriever: https://developers.llamaindex.ai/python/examples/retrievers/auto_merging_retriever/

## 🎉 Summary

```python
# That's it! Three lines for hierarchical retrieval:
from hierarchical_retriever import get_claim_retriever
retriever = get_claim_retriever()
nodes = retriever.retrieve("your query")
```

**Simple to use, powerful results!** 🚀
