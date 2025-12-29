# Auto-Merging Retriever - Visual Guide

## 🎯 Understanding Auto-Merging

This visual guide explains how the AutoMergingRetriever works step-by-step.

## 📚 The Hierarchy

### Document Structure

```
┌─────────────────────────────────────────────────────────┐
│                    ORIGINAL PDF                         │
│                 (insurance_claim_case.pdf)              │
└─────────────────────────────────────────────────────────┘
                           │
                           ↓
              HierarchicalNodeParser
                           │
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    PARSED HIERARCHY                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Level 1: ROOT NODES (2048 chars)                       │
│  ┌────────────────────────────────────────────┐         │
│  │  Root-1                                     │         │
│  │  ┌─────────┐  ┌─────────┐  ┌──────────┐  │         │
│  │  │ Mid-1   │  │ Mid-2   │  │  Mid-3   │  │         │
│  │  │         │  │         │  │          │  │         │
│  │  │ ┌─┬─┬─┐ │  │ ┌─┬─┬─┐ │  │ ┌─┬─┬─┐ │  │         │
│  │  │ └─┴─┴─┘ │  │ └─┴─┴─┘ │  │ └─┴─┴─┘ │  │         │
│  │  │ Leaves  │  │ Leaves  │  │ Leaves  │  │         │
│  │  └─────────┘  └─────────┘  └──────────┘  │         │
│  └────────────────────────────────────────────┘         │
│                                                          │
│  Level 2: MID NODES (512 chars)                         │
│  ┌──────┐  ┌──────┐  ┌──────┐                          │
│  │Mid-1 │  │Mid-2 │  │Mid-3 │                          │
│  └───┬──┘  └───┬──┘  └───┬──┘                          │
│      │         │         │                              │
│  Level 3: LEAF NODES (128 chars)                       │
│  ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐                        │
│  │L1│ │L2│ │L3│ │L4│ │L5│ │L6│ ...                    │
│  └──┘ └──┘ └──┘ └──┘ └──┘ └──┘                        │
└─────────────────────────────────────────────────────────┘
```

## 💾 Storage Layout

### What Goes Where

```
ALL NODES                           LEAF NODES ONLY
(Parents + Children)                (Smallest Chunks)
        │                                  │
        ↓                                  ↓
┌──────────────────┐              ┌────────────────────┐
│                  │              │                    │
│ SimpleDocstore   │              │ SupabaseVectorStore│
│  (In-Memory)     │              │  (PostgreSQL)      │
│                  │              │                    │
│ Stores:          │              │ Stores:            │
│  • Root nodes    │              │  • Leaf nodes only │
│  • Mid nodes     │              │  • With embeddings │
│  • Leaf nodes    │              │  • For similarity  │
│  • Hierarchy     │              │    search          │
│    relationships │              │                    │
│                  │              │                    │
└──────────────────┘              └────────────────────┘
```

## 🔍 Retrieval Process

### Step-by-Step Example

**Query:** "What is the claim date?"

#### Step 1: Similarity Search

```
Query Embedding
      │
      ↓
Vector Similarity Search in Supabase
      │
      ↓
┌─────────────────────────────────────┐
│  Top 6 Most Similar Leaf Nodes      │
├─────────────────────────────────────┤
│  [L1] Score: 0.89 → Parent: Mid-1  │
│  [L2] Score: 0.87 → Parent: Mid-1  │
│  [L3] Score: 0.85 → Parent: Mid-1  │
│  [L4] Score: 0.83 → Parent: Mid-1  │
│  [L5] Score: 0.75 → Parent: Mid-2  │
│  [L6] Score: 0.72 → Parent: Mid-3  │
└─────────────────────────────────────┘
```

#### Step 2: Auto-Merge Detection

```
Analyze Retrieved Nodes
      │
      ↓
┌─────────────────────────────────────┐
│  Grouping by Parent                 │
├─────────────────────────────────────┤
│                                     │
│  Mid-1 (Parent of L1, L2, L3, L4)  │
│  ┌───┐ ┌───┐ ┌───┐ ┌───┐          │
│  │L1 │ │L2 │ │L3 │ │L4 │          │
│  └───┘ └───┘ └───┘ └───┘          │
│  └─────┬──────────┬─────┘          │
│        │  4 nodes │                │
│        │ → MERGE! │                │
│        └──────────┘                │
│                                     │
│  Mid-2 (Parent of L5 only)         │
│  ┌───┐                              │
│  │L5 │ → Keep as leaf              │
│  └───┘                              │
│                                     │
│  Mid-3 (Parent of L6 only)         │
│  ┌───┐                              │
│  │L6 │ → Keep as leaf              │
│  └───┘                              │
│                                     │
└─────────────────────────────────────┘
```

#### Step 3: Merge & Return

```
BEFORE MERGE (6 nodes):
┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
│ L1 │ │ L2 │ │ L3 │ │ L4 │ │ L5 │ │ L6 │
│128c│ │128c│ │128c│ │128c│ │128c│ │128c│
└────┘ └────┘ └────┘ └────┘ └────┘ └────┘

         ↓ AUTO-MERGE ↓

AFTER MERGE (3 nodes):
┌──────────────────┐ ┌────┐ ┌────┐
│     Mid-1        │ │ L5 │ │ L6 │
│  (merged from    │ │128c│ │128c│
│   L1+L2+L3+L4)   │ └────┘ └────┘
│     512 chars    │
└──────────────────┘

Result: 
✓ Same relevance
✓ Better context
✓ More coherent information
```

## 🎬 Real Example

### Scenario: Querying Insurance Claim

```
Query: "When was the incident reported?"

┌──────────────────────────────────────────────────┐
│ STEP 1: RETRIEVE LEAF NODES                      │
├──────────────────────────────────────────────────┤
│                                                  │
│ Leaf Node 1 (Score: 0.91):                      │
│ "The incident was reported on February 16,      │
│  2024, one day after the incident occurred."    │
│                                                  │
│ Leaf Node 2 (Score: 0.89):                      │
│ "The claimant contacted the insurance           │
│  company immediately after discovering..."       │
│                                                  │
│ Leaf Node 3 (Score: 0.88):                      │
│ "Documentation was submitted including           │
│  photos and repair estimates."                   │
│                                                  │
│ Leaf Node 4 (Score: 0.86):                      │
│ "The claim was assigned number CLM-2024-001234." │
│                                                  │
│ [All 4 nodes have same parent: Mid-Node-A]      │
│                                                  │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│ STEP 2: AUTO-MERGE                               │
├──────────────────────────────────────────────────┤
│                                                  │
│ Detecting: 4 leaf nodes share parent Mid-Node-A │
│ Action: Merge into parent for better context    │
│                                                  │
└──────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────┐
│ STEP 3: RETURN MERGED NODE                       │
├──────────────────────────────────────────────────┤
│                                                  │
│ Mid-Node-A (512 chars):                         │
│ "The incident was reported on February 16,       │
│  2024, one day after the incident occurred.      │
│  The claimant contacted the insurance company    │
│  immediately after discovering the damage and    │
│  submitted all required documentation including  │
│  photos and repair estimates. The claim was      │
│  assigned number CLM-2024-001234 and processed   │
│  through the standard claims workflow."          │
│                                                  │
│ ✓ Complete context                               │
│ ✓ Coherent narrative                             │
│ ✓ All relevant details                           │
│                                                  │
└──────────────────────────────────────────────────┘
```

## 🔀 Merge Decision Logic

### When to Merge

```
┌─────────────────────────────────────────┐
│  For each retrieved leaf node:          │
│                                          │
│  1. Check parent node                   │
│  2. Count siblings in result set        │
│  3. If siblings > threshold:            │
│     → MERGE into parent                 │
│     Else:                                │
│     → KEEP as leaf                       │
│                                          │
└─────────────────────────────────────────┘
```

### Example Threshold Behavior

```
Threshold: 2 siblings

Case A: 4 siblings retrieved
┌───┐ ┌───┐ ┌───┐ ┌───┐
│L1 │ │L2 │ │L3 │ │L4 │  → Same parent
└───┘ └───┘ └───┘ └───┘
         ↓
┌───────────────┐
│    MERGED     │  ✓ 4 > threshold
└───────────────┘

Case B: 1 sibling retrieved
┌───┐
│L1 │  → Only one from this parent
└───┘
  ↓
┌───┐
│L1 │  ✓ Keep as leaf (1 < threshold)
└───┘
```

## 📊 Comparison: Before vs After

### Traditional Retrieval (No Merging)

```
Query → Vector Search → Return Top 6 Chunks

Result:
[Chunk 1: 128 chars] Score: 0.89
[Chunk 2: 128 chars] Score: 0.87
[Chunk 3: 128 chars] Score: 0.85
[Chunk 4: 128 chars] Score: 0.83
[Chunk 5: 128 chars] Score: 0.75
[Chunk 6: 128 chars] Score: 0.72

Total: 768 chars across 6 fragments
Problem: Context scattered across small chunks
```

### Auto-Merging Retrieval

```
Query → Vector Search → Auto-Merge → Return

Result:
[Merged Parent: 512 chars] Score: 0.89 (from L1-L4)
[Chunk 5: 128 chars] Score: 0.75
[Chunk 6: 128 chars] Score: 0.72

Total: 768 chars across 3 chunks
Benefit: Better context coherence!
```

## 🎯 Benefits Visualization

### Context Quality

```
TRADITIONAL CHUNKS:
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│ ... │ │ ... │ │ ... │ │ ... │
│claim│ │was  │ │filed│ │on...│
└─────┘ └─────┘ └─────┘ └─────┘
   ↑        ↑        ↑        ↑
Fragmented context - hard to understand

AUTO-MERGED:
┌─────────────────────────────────────┐
│ The claim was filed on February 16, │
│ 2024, with complete documentation.  │
│ All required forms were submitted.  │
└─────────────────────────────────────┘
   ↑
Complete context - easy to understand
```

## 🔧 Configuration Impact

### Small Chunks (More Precision)

```
chunk_sizes=[1024, 256, 64]

More leaf nodes → More merging opportunities
Better for: Precise fact-finding
```

### Large Chunks (More Context)

```
chunk_sizes=[4096, 1024, 256]

Fewer leaf nodes → Less merging needed
Better for: Broad understanding
```

### Default (Balanced)

```
chunk_sizes=[2048, 512, 128]

Good balance of precision and context
Best for: General purpose retrieval
```

## 💡 Key Insights

### 1. Adaptive Context

```
Simple Query → Few siblings → Keep small chunks
Complex Query → Many siblings → Merge to larger chunks

The system ADAPTS to your query!
```

### 2. Efficiency

```
Store: Only leaf nodes (128 chars) with embeddings
Retrieve: Start from leaves
Expand: Merge into parents when beneficial

Efficient storage + flexible retrieval
```

### 3. Semantic Coherence

```
┌──────────────────────────────────┐
│ Without Merging:                 │
│ "...claim date..."               │
│ "...February 16..."              │
│ "...2024..."                     │
│ ❌ Fragmented                    │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ With Merging:                    │
│ "The claim was filed on          │
│  February 16, 2024..."           │
│ ✅ Coherent                      │
└──────────────────────────────────┘
```

## 🎓 Summary

The AutoMergingRetriever intelligently combines the best of both worlds:

- **Precision**: Small leaf chunks for accurate similarity search
- **Context**: Auto-merges into larger parents for coherent results
- **Adaptability**: Merges based on actual retrieval patterns
- **Efficiency**: Only indexes smallest chunks, expands when needed

**Result**: Better answers with richer context! 🚀

## 📚 Learn More

- Full implementation: `hierarchical_retriever.py`
- Complete guide: `HIERARCHICAL_RETRIEVER_GUIDE.md`
- Quick reference: `HIERARCHICAL_QUICK_REFERENCE.md`
- LlamaIndex docs: https://developers.llamaindex.ai/
