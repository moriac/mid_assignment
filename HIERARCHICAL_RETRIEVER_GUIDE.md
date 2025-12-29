# Hierarchical Auto-Merging Retriever Setup

This guide explains how to use the hierarchical auto-merging retriever for the insurance claim PDF, implemented using LlamaIndex's `AutoMergingRetriever` pattern.

## Overview

The hierarchical retriever uses a 3-level chunk hierarchy to enable more flexible and context-aware retrieval:

- **Level 1 (Root)**: 2048 characters - Broad context
- **Level 2 (Mid)**: 512 characters - Intermediate context  
- **Level 3 (Leaf)**: 128 characters - Fine-grained chunks

### How It Works

1. **Hierarchical Parsing**: The `HierarchicalNodeParser` splits the PDF into a hierarchy of chunks
2. **Leaf Node Indexing**: Only the smallest chunks (128 chars) are embedded and stored in Supabase
3. **Auto-Merging**: During retrieval, when multiple leaf nodes from the same parent are retrieved, they're automatically merged into their parent node, providing more context

This approach balances precision (small chunks for accurate retrieval) with context (larger merged chunks for better understanding).

## Prerequisites

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The following LlamaIndex packages have been added to `requirements.txt`:
- `llama-index>=0.9.0` - Core LlamaIndex library
- `llama-index-core>=0.9.0` - Core components
- `llama-index-llms-openai>=0.1.0` - OpenAI LLM integration
- `llama-index-embeddings-openai>=0.1.0` - OpenAI embeddings
- `llama-index-vector-stores-supabase>=0.1.0` - Supabase vector store
- `llama-index-readers-file>=0.1.0` - PDF readers

### 2. Environment Variables

Ensure your `.env` file contains:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_key
SUPABASE_DB_PASSWORD=your_database_password  # Required for direct PostgreSQL connection
```

**Important**: You need to add `SUPABASE_DB_PASSWORD` to your `.env` file. You can find this in your Supabase project settings under "Database" → "Connection string".

### 3. Database Setup

Run the SQL script in your Supabase SQL Editor:

```sql
-- Copy and paste the contents of setup_hierarchical_chunks_table.sql
```

Or use the Supabase CLI:

```bash
supabase db push setup_hierarchical_chunks_table.sql
```

This creates:
- `hierarchical_chunks` table with pgvector support
- Indexes for fast similarity search
- Helper functions for searching and statistics

## Usage

### Basic Usage

```python
from hierarchical_retriever import get_claim_retriever

# Get a ready-to-use retriever (cached after first call)
retriever = get_claim_retriever()

# Retrieve relevant nodes for a query
nodes = retriever.retrieve("What is the claim amount?")

# Print retrieved nodes
for node in nodes:
    print(f"Score: {node.score:.4f}")
    print(f"Text: {node.text[:200]}...")
    print("-" * 60)
```

### With Query Engine

```python
from hierarchical_retriever import get_claim_retriever
from llama_index.core.query_engine import RetrieverQueryEngine

# Get retriever
retriever = get_claim_retriever()

# Create query engine
query_engine = RetrieverQueryEngine.from_args(retriever)

# Ask questions
response = query_engine.query("Summarize the insurance claim details")
print(response)
```

### Advanced Usage

```python
from hierarchical_retriever import HierarchicalClaimRetriever

# Custom configuration
retriever_manager = HierarchicalClaimRetriever(
    pdf_path="insurance_claim_case.pdf",
    table_name="hierarchical_chunks",
    chunk_sizes=[2048, 512, 128]  # Custom hierarchy
)

# Build the complete pipeline
retriever = retriever_manager.build_all()

# Use the retriever
nodes = retriever.retrieve("claim date", similarity_top_k=6)
```

### Rebuild Index

If you need to rebuild the index (e.g., after updating the PDF):

```python
from hierarchical_retriever import get_claim_retriever

# Force rebuild
retriever = get_claim_retriever(rebuild=True)
```

## Architecture

### Components

1. **HierarchicalNodeParser**: Splits documents into hierarchical chunks
   - Creates parent-child relationships between chunks
   - Default sizes: 2048 (parent) → 512 (mid) → 128 (leaf)

2. **SimpleDocumentStore**: Stores ALL nodes (parents + children)
   - Required for auto-merging functionality
   - Keeps hierarchy information in memory

3. **SupabaseVectorStore**: Stores ONLY leaf node embeddings
   - Uses pgvector for similarity search
   - Optimized for fast retrieval

4. **AutoMergingRetriever**: Smart retrieval with context expansion
   - Retrieves leaf nodes via similarity search
   - Automatically merges siblings into parents when beneficial
   - Provides larger context chunks when needed

### Data Flow

```
PDF Document
    ↓
HierarchicalNodeParser
    ↓
Node Hierarchy (2048/512/128)
    ↓
    ├─→ ALL nodes → SimpleDocumentStore (in-memory)
    └─→ LEAF nodes → SupabaseVectorStore (embedded)
    ↓
VectorStoreIndex
    ↓
AutoMergingRetriever
    ↓
Query Results (with auto-merged context)
```

## API Reference

### `get_claim_retriever(rebuild=False, pdf_path="insurance_claim_case.pdf", **kwargs)`

Main entry point for getting a retriever instance.

**Parameters:**
- `rebuild` (bool): Force rebuild even if cached instance exists
- `pdf_path` (str): Path to the PDF file
- `**kwargs`: Additional arguments for `HierarchicalClaimRetriever`

**Returns:**
- `AutoMergingRetriever`: Ready-to-use retriever

### `HierarchicalClaimRetriever`

Main class for managing hierarchical indexing.

**Methods:**
- `__init__(pdf_path, table_name, chunk_sizes)`: Initialize
- `load_pdf()`: Load and parse PDF
- `build_hierarchy(documents)`: Create node hierarchy
- `setup_storage(all_nodes)`: Set up docstore and vector store
- `build_index(leaf_nodes)`: Create vector index
- `create_retriever(similarity_top_k, verbose)`: Create AutoMergingRetriever
- `build_all()`: Complete pipeline

### `demo_retrieval(query)`

Demonstrate the retriever with a sample query.

## Troubleshooting

### "Missing SUPABASE_DB_PASSWORD"

The hierarchical retriever needs direct PostgreSQL access to Supabase. Add your database password to `.env`:

1. Go to Supabase Dashboard → Project Settings → Database
2. Copy the password from the connection string
3. Add to `.env`: `SUPABASE_DB_PASSWORD=your_password`

### "PDF file not found"

Ensure `insurance_claim_case.pdf` is in the project root directory, or specify the correct path:

```python
retriever = get_claim_retriever(pdf_path="path/to/your/file.pdf")
```

### Large Memory Usage

The docstore keeps all nodes in memory. For very large documents, you may need to:
- Reduce chunk sizes
- Process documents in batches
- Use a persistent docstore implementation

### Slow Initial Build

The first build involves:
- Parsing the PDF
- Creating hierarchical chunks
- Generating embeddings
- Storing in Supabase

This is cached, so subsequent calls to `get_claim_retriever()` are instant.

## Comparison with Simple Retrieval

### Simple Retrieval (existing `small_chunks` table)
- Single chunk size
- Direct similarity search
- Fixed context window

### Hierarchical Auto-Merging Retrieval
- Multi-level chunks
- Adaptive context expansion
- Auto-merges related chunks for better context
- Better for complex queries requiring broader context

## Integration with Existing Code

The hierarchical retriever can be used alongside your existing agents:

```python
from hierarchical_retriever import get_claim_retriever
from llama_index.core.query_engine import RetrieverQueryEngine

# Get hierarchical retriever
retriever = get_claim_retriever()

# Create query engine
query_engine = RetrieverQueryEngine.from_args(retriever)

# Use in your agent
def enhanced_agent_task(query: str):
    # Get context from hierarchical retriever
    response = query_engine.query(query)
    context = str(response)
    
    # Use context in your agent
    # ... your existing agent code ...
    
    return result
```

## Performance Tips

1. **Caching**: Use `get_claim_retriever()` without `rebuild=True` to use cached instance
2. **Similarity Top K**: Adjust `similarity_top_k` based on your needs (default: 6)
3. **Chunk Sizes**: Experiment with different hierarchy levels for your use case
4. **Verbose Mode**: Set `verbose=False` in production to reduce console output

## Example Queries

```python
from hierarchical_retriever import demo_retrieval

# Run demo with different queries
demo_retrieval("What is the claim date?")
demo_retrieval("Summarize the incident details")
demo_retrieval("What is the policy number?")
demo_retrieval("List all damages mentioned")
```

## Next Steps

1. Run the demo: `python hierarchical_retriever.py`
2. Integrate with your agents
3. Experiment with different chunk sizes
4. Compare results with simple retrieval
5. Optimize for your specific use case

## References

- [LlamaIndex AutoMergingRetriever Documentation](https://developers.llamaindex.ai/python/examples/retrievers/auto_merging_retriever/)
- [HierarchicalNodeParser API](https://docs.llamaindex.ai/en/stable/api_reference/node_parsers/)
- [Supabase Vector Store](https://docs.llamaindex.ai/en/stable/examples/vector_stores/SupabaseVectorIndexDemo/)
