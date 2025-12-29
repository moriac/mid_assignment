# Hierarchical Auto-Merging Retriever Implementation

This implementation provides a hierarchical retrieval system for the `insurance_claim_case.pdf` file using LlamaIndex's AutoMergingRetriever pattern.

## 🎯 What This Does

Creates a **smart hierarchical retrieval system** that:

1. **Parses the PDF** into a 3-level chunk hierarchy (2048/512/128 characters)
2. **Stores embeddings** of small leaf chunks in Supabase vector store
3. **Auto-merges** retrieved chunks into larger parent chunks when beneficial
4. **Provides better context** by intelligently expanding from precise matches to broader context

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

Create/update `.env` with:

```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
SUPABASE_DB_PASSWORD=your_database_password
```

### 3. Set Up Database

Run `setup_hierarchical_chunks_table.sql` in Supabase SQL Editor.

### 4. Run the Demo

```bash
python hierarchical_retriever.py
```

Or use the quick start:

```bash
python quick_start_hierarchical.py
```

## 📁 Files Created

| File | Purpose |
|------|---------|
| `hierarchical_retriever.py` | Main implementation with `get_claim_retriever()` |
| `setup_hierarchical_chunks_table.sql` | Supabase table schema |
| `HIERARCHICAL_RETRIEVER_GUIDE.md` | Complete documentation |
| `test_hierarchical_retriever.py` | Test suite |
| `quick_start_hierarchical.py` | Simple usage example |
| `requirements.txt` | Updated with LlamaIndex dependencies |

## 💡 Usage Examples

### Basic Retrieval

```python
from hierarchical_retriever import get_claim_retriever

# Get retriever (cached after first call)
retriever = get_claim_retriever()

# Retrieve nodes
nodes = retriever.retrieve("What is the claim amount?")

for node in nodes:
    print(node.text)
```

### With Query Engine

```python
from hierarchical_retriever import get_claim_retriever
from llama_index.core.query_engine import RetrieverQueryEngine

retriever = get_claim_retriever()
query_engine = RetrieverQueryEngine.from_args(retriever)

response = query_engine.query("Summarize the claim")
print(response)
```

### Custom Configuration

```python
from hierarchical_retriever import HierarchicalClaimRetriever

retriever_manager = HierarchicalClaimRetriever(
    pdf_path="insurance_claim_case.pdf",
    chunk_sizes=[2048, 512, 128]
)

retriever = retriever_manager.build_all()
```

## 🏗️ Architecture

```
insurance_claim_case.pdf
         ↓
HierarchicalNodeParser (2048/512/128)
         ↓
    ┌────────┴────────┐
    ↓                 ↓
All Nodes        Leaf Nodes
    ↓                 ↓
SimpleDocumentStore  SupabaseVectorStore
    ↓                 ↓
    └────────┬────────┘
             ↓
    VectorStoreIndex
             ↓
   AutoMergingRetriever
             ↓
   Smart Context Retrieval
```

## 🔑 Key Components

### 1. HierarchicalNodeParser
- Splits document into 3 levels
- Default: 2048 (root) → 512 (mid) → 128 (leaf)
- Maintains parent-child relationships

### 2. SimpleDocumentStore
- Stores ALL nodes (parents + children)
- Required for auto-merging
- In-memory storage

### 3. SupabaseVectorStore
- Stores ONLY leaf node embeddings
- Fast similarity search with pgvector
- Persistent storage

### 4. AutoMergingRetriever
- Retrieves leaf nodes via similarity
- Auto-merges siblings into parents
- Adaptive context expansion

## 📊 Comparison: Simple vs. Hierarchical

| Feature | Simple Chunks | Hierarchical Auto-Merge |
|---------|---------------|-------------------------|
| Chunk Size | Fixed (single level) | Adaptive (3 levels) |
| Context | Fixed window | Auto-expanding |
| Retrieval | Direct match | Match + merge parents |
| Best For | Simple queries | Complex queries needing context |
| Memory | Lower | Higher (docstore) |
| Accuracy | Good | Better for context-dependent queries |

## 🧪 Testing

Run the test suite:

```bash
python test_hierarchical_retriever.py
```

Tests include:
- ✓ Package imports
- ✓ Environment variables
- ✓ PDF file exists
- ✓ Hierarchical parsing
- ✓ Supabase connection
- ✓ Demo retrieval

## 🔧 API Reference

### `get_claim_retriever(rebuild=False, pdf_path="insurance_claim_case.pdf", **kwargs)`

Main entry point. Returns a ready-to-use `AutoMergingRetriever`.

**Parameters:**
- `rebuild` (bool): Force rebuild
- `pdf_path` (str): Path to PDF
- `**kwargs`: Additional config

**Returns:**
- `AutoMergingRetriever`

### `HierarchicalClaimRetriever`

Main class for managing the retrieval system.

**Key Methods:**
- `build_all()`: Complete pipeline
- `load_pdf()`: Load and parse PDF
- `build_hierarchy()`: Create node hierarchy
- `create_retriever()`: Get AutoMergingRetriever

## 📝 Example Queries

```python
from hierarchical_retriever import demo_retrieval

# Demo different queries
demo_retrieval("What is the claim date?")
demo_retrieval("Summarize the incident")
demo_retrieval("What damages were claimed?")
demo_retrieval("What is the policy number?")
```

## 🐛 Troubleshooting

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Missing Environment Variable
```
Error: Missing Supabase credentials
```
→ Add to `.env`: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_DB_PASSWORD`

### PDF Not Found
```
Error: PDF file not found
```
→ Ensure `insurance_claim_case.pdf` is in project root

### Database Error
```
Error: relation "hierarchical_chunks" does not exist
```
→ Run `setup_hierarchical_chunks_table.sql` in Supabase

## 🎓 How Auto-Merging Works

1. **Query**: "What is the claim date?"
2. **Similarity Search**: Retrieves 6 leaf nodes (128 chars each)
3. **Auto-Merge Detection**: Finds 4 leaf nodes with same parent
4. **Merge**: Combines those 4 into 1 parent node (512 chars)
5. **Result**: Returns 3 nodes instead of 6, with better context

**Before Merge:**
```
[Leaf 1] [Leaf 2] [Leaf 3] [Leaf 4] [Leaf 5] [Leaf 6]
(128)    (128)    (128)    (128)    (128)    (128)
```

**After Merge:**
```
[Parent of 1-4]  [Leaf 5]  [Leaf 6]
(512 chars)      (128)     (128)
```

→ Same relevance, more context!

## 📚 Documentation

For detailed documentation, see:
- `HIERARCHICAL_RETRIEVER_GUIDE.md` - Complete guide
- `setup_hierarchical_chunks_table.sql` - Database schema
- [LlamaIndex AutoMergingRetriever Docs](https://developers.llamaindex.ai/python/examples/retrievers/auto_merging_retriever/)

## 🔄 Integration with Existing Code

The hierarchical retriever works alongside your existing code:

```python
# Your existing agent
from summarization_expert_agent import SummarizationExpertAgent
from hierarchical_retriever import get_claim_retriever
from llama_index.core.query_engine import RetrieverQueryEngine

# Get hierarchical retriever
retriever = get_claim_retriever()
query_engine = RetrieverQueryEngine.from_args(retriever)

# Use in your workflow
def enhanced_workflow(query):
    # Get hierarchical context
    context = query_engine.query(query)
    
    # Use with existing agent
    agent = SummarizationExpertAgent()
    result = agent.answer(query, context=str(context))
    
    return result
```

## ⚡ Performance Tips

1. **Caching**: First build takes time; subsequent calls are instant
2. **Similarity Top K**: Adjust based on needs (default: 6)
3. **Chunk Sizes**: Experiment with different hierarchies
4. **Verbose Mode**: Disable in production (`verbose=False`)

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Set up environment
3. ✅ Run Supabase SQL script
4. ✅ Test with `python test_hierarchical_retriever.py`
5. ✅ Run demo with `python hierarchical_retriever.py`
6. ✅ Integrate with your agents
7. ✅ Optimize for your use case

## 📄 License

Same as parent project.

## 🤝 Contributing

This implementation follows the LlamaIndex AutoMergingRetriever pattern from:
https://developers.llamaindex.ai/python/examples/retrievers/auto_merging_retriever/

---

**Built with ❤️ using LlamaIndex and Supabase**
