# Hierarchical Retrieval Integration with Specific Task Expert Agent

## Overview

The Specific Task Expert Agent has been successfully integrated with the **Hierarchical Auto-Merging Retrieval System** (LlamaIndex). This integration replaces the previous direct Supabase query approach with an intelligent, context-aware retrieval mechanism.

## What Changed

### Before Integration
- Used `get_top_k_chunks_from_small_chunks()` from `supabase_utils.py`
- Retrieved fixed-size chunks directly from Supabase `small_chunks` table
- No intelligent context merging
- Static chunk sizes

### After Integration
- Uses `get_claim_retriever()` from `hierarchical_retriever.py`
- Implements LlamaIndex's AutoMergingRetriever
- Intelligent hierarchical chunk merging (128 → 512 → 2048 characters)
- Dynamic context assembly based on query relevance

## Key Benefits

### 1. **Intelligent Context Assembly**
- The retriever automatically merges smaller chunks into larger parent chunks when they're all relevant
- Provides more coherent context to the LLM
- Reduces fragmentation in retrieved information

### 2. **Better Semantic Understanding**
- Uses hierarchical node structure for improved semantic relationships
- Maintains document structure and context flow
- Prevents loss of context across chunk boundaries

### 3. **Optimized Retrieval**
- Retrieves at the leaf level (128 chars) for precision
- Merges to parent levels (512, 2048 chars) for context
- Balances specificity with comprehensiveness

### 4. **Maintained Compatibility**
- All MCP tools (date calculations, compliance checks) still work
- Same agent interface and API
- Backward compatible with existing code

## Architecture

```
┌─────────────────────────────────────────────┐
│    Specific Task Expert Agent               │
│                                             │
│  ┌────────────────────────────────────┐   │
│  │ User Query                          │   │
│  └───────────┬────────────────────────┘   │
│              │                             │
│              ▼                             │
│  ┌────────────────────────────────────┐   │
│  │ Hierarchical Retriever              │   │
│  │ (AutoMergingRetriever)             │   │
│  └───────────┬────────────────────────┘   │
│              │                             │
│              ▼                             │
│  ┌────────────────────────────────────┐   │
│  │ Retrieved Nodes (Auto-Merged)      │   │
│  └───────────┬────────────────────────┘   │
│              │                             │
│              ▼                             │
│  ┌────────────────────────────────────┐   │
│  │ LLM with Context + MCP Tools       │   │
│  └───────────┬────────────────────────┘   │
│              │                             │
│              ▼                             │
│  ┌────────────────────────────────────┐   │
│  │ Precise Answer                      │   │
│  └────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

## Code Changes

### 1. Import Updates
```python
# OLD
from supabase_utils import get_top_k_chunks_from_small_chunks

# NEW
from hierarchical_retriever import get_claim_retriever
```

### 2. Agent Initialization
```python
def __init__(self, model_name="gpt-3.5-turbo", temperature=0, use_hierarchical_retrieval=True):
    # ... existing code ...
    
    # NEW: Initialize hierarchical retriever
    self.use_hierarchical_retrieval = use_hierarchical_retrieval
    self.hierarchical_retriever = None
    if use_hierarchical_retrieval:
        print("Initializing hierarchical auto-merging retrieval system...")
        try:
            self.hierarchical_retriever = get_claim_retriever(use_supabase=False)
            print("✓ Hierarchical retriever ready")
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize hierarchical retriever: {e}")
            self.use_hierarchical_retrieval = False
```

### 3. Retrieval Logic
```python
# OLD
relevant_chunks = get_top_k_chunks_from_small_chunks(user_input, k=3)
context_str = "\n---\n".join(relevant_chunks) if relevant_chunks else None

# NEW
context_str = None
if self.use_hierarchical_retrieval and self.hierarchical_retriever:
    print(f"\n🔍 Retrieving context using hierarchical auto-merging retrieval...")
    retrieved_nodes = self.hierarchical_retriever.retrieve(user_input)
    
    if retrieved_nodes:
        print(f"   Retrieved {len(retrieved_nodes)} node(s) after auto-merging")
        relevant_chunks = [node.text for node in retrieved_nodes]
        context_str = "\n---\n".join(relevant_chunks)
```

## Usage

### Basic Usage
```python
from specific_task_expert_agent import SpecificTaskExpertAgent

# Initialize agent with hierarchical retrieval (default)
agent = SpecificTaskExpertAgent()

# Process a query
response = agent.process_specific_question("What is the claim date?")
print(response)
```

### Advanced Usage
```python
# Disable hierarchical retrieval if needed
agent = SpecificTaskExpertAgent(use_hierarchical_retrieval=False)

# Use different model
agent = SpecificTaskExpertAgent(
    model_name="gpt-4",
    temperature=0,
    use_hierarchical_retrieval=True
)
```

## Testing

Run the integration test:
```bash
python test_specific_task_hierarchical.py
```

Test output shows:
- Hierarchical retriever initialization
- Auto-merging in action (e.g., "Merging 3 nodes into parent node")
- Number of nodes retrieved after merging
- MCP tool usage (if applicable)
- Final LLM answers

## Performance

### Retrieval Metrics (Example)
- **Query**: "What is the claim date?"
- **Initial leaf nodes retrieved**: 6
- **After auto-merging**: 6 nodes (2 merged into parent)
- **Total context size**: ~2000-4000 characters
- **Response time**: ~2-3 seconds (including embeddings + LLM)

### Auto-Merging Examples

#### Example 1: Related chunks merged
```
Query: "Who is the policyholder?"
- Initial: 6 leaf nodes (128 chars each)
- Merged: 4 nodes (3 merged into 1 parent node of 512 chars)
- Benefit: Related policy information kept together
```

#### Example 2: Distributed information
```
Query: "What is the claim amount?"
- Initial: 6 leaf nodes
- Merged: 6 nodes (no merging needed)
- Benefit: Specific dollar amount found precisely
```

## Comparison: Old vs New

| Aspect | Old (Supabase Direct) | New (Hierarchical) |
|--------|----------------------|-------------------|
| **Chunk Size** | Fixed (small) | Dynamic (128→512→2048) |
| **Context Quality** | Fragmented | Coherent & merged |
| **Semantic Understanding** | Limited | Enhanced |
| **Storage** | Supabase table | In-memory (default) |
| **Performance** | Fast, simple | Slightly slower, intelligent |
| **Context Preservation** | May lose context | Preserves relationships |
| **Setup Complexity** | Minimal | Moderate (one-time) |

## Configuration Options

### In-Memory vs Supabase Storage

**Default (In-Memory):**
```python
agent = SpecificTaskExpertAgent()  # Uses in-memory vector store
```

**Supabase Storage:**
```python
# Requires SUPABASE_DB_PASSWORD in .env
from hierarchical_retriever import get_claim_retriever

# In agent initialization, configure retriever separately
retriever = get_claim_retriever(use_supabase=True)
```

### Chunk Sizes

Default hierarchy: `[2048, 512, 128]`

To customize:
```python
from hierarchical_retriever import HierarchicalClaimRetriever

custom_retriever = HierarchicalClaimRetriever(
    chunk_sizes=[4096, 1024, 256]  # Larger chunks
)
retriever = custom_retriever.build_all()
```

### Similarity Top K

Default: 6 leaf nodes retrieved

To customize:
```python
retriever = HierarchicalClaimRetriever()
# ... build steps ...
retriever.create_retriever(similarity_top_k=10)  # More nodes
```

## Troubleshooting

### Issue: Retriever initialization fails
**Solution**: Ensure `insurance_claim_case.pdf` is in the project directory
```bash
# Check for PDF
dir insurance_claim_case.pdf
```

### Issue: No context retrieved
**Symptoms**: "No relevant nodes found" message
**Solution**: 
1. Verify PDF has content
2. Check OpenAI API key is valid
3. Try rebuilding the index:
   ```python
   from hierarchical_retriever import get_claim_retriever
   retriever = get_claim_retriever(rebuild=True)
   ```

### Issue: Slow retrieval
**Cause**: Embedding generation for queries
**Solution**: Normal behavior - embeddings are required for semantic search

## Future Enhancements

### Potential Improvements
1. **Caching**: Cache retriever instance across multiple queries
2. **Hybrid Search**: Combine keyword + semantic search
3. **Re-ranking**: Add cross-encoder re-ranking for better precision
4. **Custom Merging**: Configure merge strategies per query type
5. **Supabase Integration**: Persist hierarchical chunks in Supabase

### Planned Features
- [ ] Persistent storage option with Supabase
- [ ] Query performance metrics
- [ ] Retrieval quality evaluation
- [ ] A/B testing framework (old vs new)
- [ ] Configurable merge threshold

## Dependencies

Required packages (already in `requirements.txt`):
```
llama-index-core
llama-index-embeddings-openai
llama-index-llms-openai
llama-index-readers-file
langchain-openai
python-dotenv
```

## Migration Guide

### For Existing Code

If you have existing code using the old agent:

**Before:**
```python
from specific_task_expert_agent import SpecificTaskExpertAgent
agent = SpecificTaskExpertAgent()
response = agent.process_specific_question("query")
```

**After:**
```python
# Same code - no changes needed!
from specific_task_expert_agent import SpecificTaskExpertAgent
agent = SpecificTaskExpertAgent()  # Now uses hierarchical retrieval
response = agent.process_specific_question("query")
```

**To disable hierarchical retrieval:**
```python
agent = SpecificTaskExpertAgent(use_hierarchical_retrieval=False)
```

## Conclusion

The integration successfully brings advanced hierarchical retrieval capabilities to the Specific Task Expert Agent while maintaining backward compatibility. The auto-merging feature ensures optimal context assembly, leading to more accurate and comprehensive answers for specific "needle in haystack" questions.

## References

- [Hierarchical Retriever Guide](HIERARCHICAL_RETRIEVER_GUIDE.md)
- [Hierarchical Implementation Summary](HIERARCHICAL_IMPLEMENTATION_SUMMARY.md)
- [LlamaIndex AutoMergingRetriever Documentation](https://docs.llamaindex.ai/en/stable/examples/retrievers/auto_merging_retriever/)
