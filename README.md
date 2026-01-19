# Insurance Claim RAG System# Orchestrator Agent with Summarization Expert



A sophisticated **Retrieval-Augmented Generation (RAG)** system for processing and querying insurance claim documents. This project implements a multi-agent architecture with intelligent chunking strategies, hierarchical retrieval, and MCP (Model Context Protocol) tool integration.A multi-agent system built with LangChain that intelligently classifies user questions and routes them to specialized agents.



---## 🏗️ Architecture



## 📋 Table of Contents### Two-Agent System:



- [Overview](#-overview)1. **Orchestrator Agent** (`orchestrator_agent.py`)

- [Architecture](#-architecture)   - Classifies user questions into 3 types using LLM

- [Features](#-features)   - Routes Type 2 questions to the Summarization Expert

- [Installation](#-installation)   - Coordinates the overall workflow

- [Usage](#-usage)

- [Agent System](#-agent-system)2. **Summarization Expert Agent** (`summarization_expert_agent.py`)

- [Chunking Strategies](#-chunking-strategies)   - Specialized in handling broad questions

- [MCP Tools](#-mcp-tools)   - Creates comprehensive summaries and overviews

- [ChromaDB Integration](#-chromadb-integration)   - Analyzes timelines and trends

- [LlamaIndex Integration](#-llamaindex-integration)

- [Project Structure](#-project-structure)## 📊 Question Classification

- [API Reference](#-api-reference)

The Orchestrator classifies questions into:

---

### Type 1️⃣: Needle in Haystack (Specific Questions)

## 🎯 Overview- Very precise questions requiring exact information

- Examples:

This system processes insurance claim PDF documents and enables intelligent question-answering through a multi-agent architecture. It combines:  - "What was the exact error code in line 45?"

  - "Who approved the PR on March 5th?"

- **Multi-Agent Orchestration**: Routes questions to specialized expert agents  - "What's the value of variable X in function Y?"

- **Dual Chunking Strategies**: Smart LLM-based chunking and hierarchical auto-merging

- **Vector Database Storage**: ChromaDB for efficient semantic search### Type 2️⃣: Broad Questions (Summary/Timeline)

- **MCP Tool Integration**: Date/time calculation tools for insurance compliance checking- Summary requests and overviews

- **LlamaIndex Framework**: Hierarchical node parsing with auto-merging retrieval- Timeline-oriented questions

- **Automatically routed to Summarization Expert Agent**

---- Examples:

  - "Summarize this issue"

## 🏗 Architecture  - "What happened last week?"

  - "Give me an overview of the project"

```  - "What's the status of all open tickets?"

┌─────────────────────────────────────────────────────────────────────┐

│                        User Query                                    │### Type 3️⃣: Other

└─────────────────────────────────────────────────────────────────────┘- Questions that don't fit Type 1 or 2

                                 │- General conversation, greetings, commands

                                 ▼- Examples:

┌─────────────────────────────────────────────────────────────────────┐  - "Hello", "Help", "Thank you"

│                    ORCHESTRATOR AGENT                                │  - "Calculate 2+2"

│  ┌─────────────────────────────────────────────────────────────┐   │

│  │ Question Classification (GPT-3.5-turbo)                      │   │## 🚀 Installation

│  │ • Type 1: Needle in Haystack (Specific questions)            │   │

│  │ • Type 2: Broad Questions (Summaries/Timelines)              │   │1. Install required packages:

│  │ • Type 3: Other                                              │   │

│  └─────────────────────────────────────────────────────────────┘   │```bash

└─────────────────────────────────────────────────────────────────────┘pip install -r requirements.txt

                    │                           │```

         Type 1     │                           │    Type 2

                    ▼                           ▼2. Set up your OpenAI API key:

┌─────────────────────────────┐   ┌─────────────────────────────────┐

│  SPECIFIC TASK EXPERT       │   │  SUMMARIZATION EXPERT           │**Windows (PowerShell):**

│  ┌───────────────────────┐  │   │  ┌───────────────────────────┐  │```powershell

│  │ Hierarchical Retrieval│  │   │  │ ChromaDB Vector Search    │  │$env:OPENAI_API_KEY='your_api_key_here'

│  │ (LlamaIndex)          │  │   │  │ (Smart Chunks)            │  │```

│  │ • Auto-merging        │  │   │  │ • Semantic similarity     │  │

│  │ • Metadata extraction │  │   │  │ • Section-aware chunks    │  │**Linux/Mac:**

│  └───────────────────────┘  │   │  └───────────────────────────┘  │```bash

│  ┌───────────────────────┐  │   │  ┌───────────────────────────┐  │export OPENAI_API_KEY='your_api_key_here'

│  │ MCP Tools             │  │   │  │ MCP Tools                 │  │```

│  │ • Timeline duration   │  │   │  │ • Business days calc      │  │

│  │ • Business days       │  │   │  │ • Compliance checking     │  │Or create a `.env` file:

│  │ • Policy compliance   │  │   │  └───────────────────────────┘  │```bash

│  └───────────────────────┘  │   │                                  │OPENAI_API_KEY=your_api_key_here

└─────────────────────────────┘   └─────────────────────────────────┘MODEL_NAME=gpt-3.5-turbo

                    │                           │TEMPERATURE=0.7

                    ▼                           ▼```

┌─────────────────────────────────────────────────────────────────────┐

│                         ChromaDB                                     │## 💻 Usage

│  ┌────────────────────────┐    ┌────────────────────────────────┐  │

│  │ Collection:            │    │ Collection:                     │  │### Interactive Mode

│  │ "small_chunks"         │    │ "insurance_claims"              │  │

│  │ (Hierarchical 128-char │    │ (Smart LLM chunks)              │  │Run the orchestrator agent:

│  │  leaf nodes)           │    │                                  │  │

│  └────────────────────────┘    └────────────────────────────────┘  │```bash

└─────────────────────────────────────────────────────────────────────┘python orchestrator_agent.py

``````



---### Example Interaction



## ✨ Features```

🤖 You: Summarize the key developments in AI this year

### Multi-Agent System

- **Orchestrator Agent**: Classifies incoming questions and routes to appropriate expert💭 Analyzing your question...

- **Specific Task Expert**: Handles precise "needle in haystack" questions with hierarchical retrieval

- **Summarization Expert**: Handles broad questions with semantic search╔══════════════════════════════════════════════════════════╗

║ QUESTION CLASSIFICATION RESULT                           ║

### Intelligent Document Processing╠══════════════════════════════════════════════════════════╣

- **Smart LLM Chunking**: Uses GPT-4o to intelligently segment documents by semantic sections║ Classification: 2

- **Hierarchical Chunking**: LlamaIndex-based 3-level hierarchy (2048/512/128 characters)║ Type: 📊 Type 2: Broad Question (Summary/Timeline)

- **Metadata Extraction**: Automatic extraction of dates, amounts, policy numbers, etc.║ 

║ Explanation: This is a broad summary request...

### MCP Tool Integration╚══════════════════════════════════════════════════════════╝

- **Timeline Duration Calculator**: Calculate exact time between dates

- **Business Days Calculator**: Compute working days excluding weekends🔄 Routing to Summarization Expert Agent...

- **Policy Compliance Checker**: Verify deadline compliance────────────────────────────────────────────────────────────



### Vector Database📋 SUMMARIZATION EXPERT RESPONSE:

- **ChromaDB**: Persistent vector storage with OpenAI embeddings────────────────────────────────────────────────────────────

- **Dual Collections**: Separate collections for different retrieval strategies[Comprehensive summary from Summarization Expert]

────────────────────────────────────────────────────────────

---```



## 📦 Installation### Programmatic Usage



### Prerequisites```python

- Python 3.9+from orchestrator_agent import OrchestratorAgent

- OpenAI API Key

# Initialize

### Setupagent = OrchestratorAgent(model_name="gpt-3.5-turbo")



1. **Clone the repository**# Process a question

   ```bashresponse = agent.run("Summarize the project status from last month")

   git clone <repository-url>print(response)

   cd mid_assignment```

   ```

### Test the Agents

2. **Create a virtual environment**

   ```bashRun the test script to see all question types:

   python -m venv venv

   source venv/bin/activate  # Linux/Mac```bash

   venv\Scripts\activate     # Windowspython test_agents.py

   ``````



3. **Install dependencies**## 📁 Project Structure

   ```bash

   pip install -r requirements.txt```

   ```mid_assignment/

├── orchestrator_agent.py          # Main orchestrator agent

4. **Configure environment variables**├── summarization_expert_agent.py  # Specialized summarization agent

   Create a `.env` file in the project root:├── test_agents.py                 # Test script

   ```env├── requirements.txt               # Python dependencies

   OPENAI_API_KEY=your-api-key-here├── .env.example                   # Environment template

   ```└── README.md                      # This file

```

5. **Process your PDF document**

   Place your insurance claim PDF as `insurance_claim_case.pdf` in the project root.## 🔄 Workflow



---1. **User Input** → Orchestrator Agent

2. **Classification** → LLM analyzes question type (1, 2, or 3)

## 🚀 Usage3. **Routing Decision**:

   - **Type 2** → Summarization Expert Agent → Comprehensive Response

### Quick Start   - **Type 1** → (Reserved for future needle-in-haystack agent)

   - **Type 3** → Standard handling

#### 1. Process PDF and Store in ChromaDB (Smart Chunking)4. **Response** → Formatted output to user

```bash

python chromadb_chunk_pdf.py## 🎯 Features

```

This uses GPT-4o to intelligently chunk the PDF into semantic sections and stores them in ChromaDB.### Orchestrator Agent

- ✅ Intelligent question classification using LLM

#### 2. Build Hierarchical Index (LlamaIndex)- ✅ Clear classification explanations

```bash- ✅ Automatic routing to specialist agents

python hierarchical_retriever.py- ✅ Interactive terminal interface

```- ✅ Formatted, user-friendly output

This creates a 3-level hierarchical index with auto-merging capabilities.

### Summarization Expert Agent

#### 3. Run the Orchestrator Agent- ✅ Comprehensive summaries and overviews

```bash- ✅ Timeline analysis capabilities

python orchestrator_agent.py- ✅ Multiple summary types (general, timeline, executive, technical)

```- ✅ Context-aware responses

Start the interactive agent that routes your questions to the appropriate expert.- ✅ Specialized prompting for broad questions



### Example Queries## 🛠️ Advanced Usage



**Specific Questions (Type 1 - Routed to Specific Task Expert)**:### Using Summarization Expert Directly

- "What is the claim number?"

- "When did the incident occur?"```python

- "What is the total claim amount?"from summarization_expert_agent import SummarizationExpertAgent

- "How many days elapsed between the incident and claim filing?"

agent = SummarizationExpertAgent()

**Broad Questions (Type 2 - Routed to Summarization Expert)**:

- "Summarize this insurance claim"# Process broad question

- "What is the timeline of events?"response = agent.process_broad_question("Summarize this issue")

- "Give me an overview of the investigation findings"

- "What happened during the claim process?"# Generate specific summary types

summary = agent.generate_summary(content, summary_type="timeline")

---

# Analyze timeline

## 🤖 Agent Systemtimeline = agent.analyze_timeline(events)



### Orchestrator Agent (`orchestrator_agent.py`)# Get overview

overview = agent.get_overview("Project Architecture")

The central routing agent that classifies user questions into three categories:```



```python## 🔧 Configuration

from orchestrator_agent import OrchestratorAgent

Customize the agents by passing parameters:

agent = OrchestratorAgent(model_name="gpt-3.5-turbo")

response = agent.run("What is the claim amount?")```python

```# Orchestrator with custom model

orchestrator = OrchestratorAgent(model_name="gpt-4")

**Classification Logic**:

| Category | Type | Description | Routed To |# Summarization Expert with custom settings

|----------|------|-------------|-----------|expert = SummarizationExpertAgent(

| 1 | Needle in Haystack | Specific facts, dates, numbers | Specific Task Expert |    model_name="gpt-4",

| 2 | Broad Questions | Summaries, timelines, overviews | Summarization Expert |    temperature=0.7  # More creative summaries

| 3 | Other | General conversation, commands | No specialized handling |)

```

### Specific Task Expert (`specific_task_expert_agent.py`)

## 📝 Requirements

Handles precise questions using hierarchical auto-merging retrieval:

- Python 3.8+

```python- OpenAI API key

from specific_task_expert_agent import SpecificTaskExpertAgent- Internet connection for API calls



agent = SpecificTaskExpertAgent(## 🔐 Security Notes

    model_name="gpt-3.5-turbo",

    temperature=0,  # Precise answers- Never commit your `.env` file or expose API keys

    use_hierarchical_retrieval=True- Use `.env.example` as a template only

)- Add `.env` to your `.gitignore`

response = agent.process_specific_question("What is the policy number?")- Revoke any exposed API keys immediately

```

## 🎓 Example Use Cases

**Key Features**:

- Metadata-first answering for exact information (claim numbers, dates, amounts)1. **Project Management**: "Summarize all tickets closed last sprint"

- Hierarchical retrieval with auto-merging for complex queries2. **Code Review**: "Give me an overview of changes in the feature branch"

- MCP tool integration for date/time calculations3. **Documentation**: "What are the key components of this system?"

- Low temperature (0) for consistent, factual responses4. **Timeline Analysis**: "What happened in the development process last quarter?"



### Summarization Expert (`summarization_expert_agent.py`)## 🚧 Future Enhancements



Handles broad questions using ChromaDB vector search:- [ ] Implement Needle-in-Haystack search agent for Type 1 questions

- [ ] Add RAG (Retrieval Augmented Generation) for context

```python- [ ] Support for document/code base indexing

from summarization_expert_agent import SummarizationExpertAgent- [ ] Multi-turn conversations with memory

- [ ] Export summaries to different formats

agent = SummarizationExpertAgent(

    model_name="gpt-3.5-turbo",## 📄 License

    temperature=0.7,  # Creative but coherent

    collection_name="insurance_claims"MIT License

)

response = agent.process_broad_question("Summarize the claim")## 🤝 Contributing

```

Contributions welcome! Feel free to submit issues or pull requests.

**Key Features**:
- Vector similarity search in ChromaDB
- Retrieves top-k relevant chunks for context
- Higher temperature (0.7) for comprehensive summaries
- MCP tool integration for timeline analysis

---

## 📄 Chunking Strategies

### Strategy 1: Smart LLM Chunking (`chromadb_chunk_pdf.py`)

Uses GPT-4o to intelligently segment documents by semantic meaning:

```python
# Process flow
1. Extract PDF text using PyMuPDF
2. Send to GPT-4o with chunking prompt
3. GPT-4o returns JSON with logical sections:
   - Case overview
   - Incident description
   - Medical records
   - Claim details
   - Investigation findings
   - Decision and outcome
4. Store chunks in ChromaDB with metadata
```

**Advantages**:
- Preserves semantic coherence
- Section-aware boundaries
- Includes actual content, not generic descriptions
- Configurable section identification

**Storage**: `insurance_claims` collection in ChromaDB

### Strategy 2: Hierarchical Chunking (`hierarchical_retriever.py`)

Uses LlamaIndex's `HierarchicalNodeParser` for multi-level indexing:

```python
# Chunk size hierarchy
Level 1 (Root):   2048 characters
Level 2 (Mid):     512 characters  
Level 3 (Leaf):    128 characters

# Auto-merging behavior
- Query matches leaf nodes (128 chars)
- If multiple siblings match, merge to parent (512 chars)
- If enough children match, escalate to root (2048 chars)
```

**Advantages**:
- Fine-grained matching with small chunks
- Context preservation through auto-merging
- Parent-child relationships maintained
- Optimal for "needle in haystack" queries

**Storage**: `small_chunks` collection in ChromaDB + `docstore.json` for hierarchy

### Comparison

| Feature | Smart LLM Chunking | Hierarchical Chunking |
|---------|-------------------|----------------------|
| Method | GPT-4o semantic analysis | Fixed-size hierarchy |
| Chunk Sizes | Variable (300-1500 words) | 2048/512/128 chars |
| Best For | Summaries, overviews | Specific facts |
| Context | Section boundaries | Auto-merging parents |
| Cost | Higher (GPT-4o calls) | Lower (rule-based) |

---

## 🔧 MCP Tools

Model Context Protocol (MCP) tools provide date/time calculation capabilities bound to LangChain's tool system.

### Available Tools (`mcp/claim_date_tools.py`)

#### 1. `calculate_timeline_duration`
Calculate precise duration between two timestamps.

```python
from mcp.claim_date_tools import calculate_timeline_duration

result = calculate_timeline_duration.invoke({
    "start_datetime": "2024-01-15 09:30:00",
    "end_datetime": "2024-01-18 14:45:00"
})
# Output: "Duration: 3 days, 5 hours, 15 minutes (Total: 77.25 hours)"
```

**Use Cases**:
- "How long was the claim open?"
- "What's the duration between incident and report?"

#### 2. `calculate_business_days`
Calculate working days excluding weekends.

```python
from mcp.claim_date_tools import calculate_business_days

result = calculate_business_days.invoke({
    "start_date": "2024-01-15",
    "end_date": "2024-01-25"
})
# Output: "Business days: 8, Calendar days: 10, Weekend days: 2"
```

**Use Cases**:
- "How many business days for processing?"
- "Working days between dates?"

#### 3. `check_policy_compliance`
Verify if an event occurred within a required timeframe.

```python
from mcp.claim_date_tools import check_policy_compliance

result = check_policy_compliance.invoke({
    "event_date": "2024-01-20",
    "reference_date": "2024-01-15",
    "deadline_days": 30
})
# Output: "COMPLIANT: Event occurred 5 days after reference date..."
```

**Use Cases**:
- "Was the claim filed within 30 days?"
- "Check notification deadline compliance"

### Tool Binding

Tools are automatically bound to the LLM in each agent:

```python
from langchain_openai import ChatOpenAI
from mcp.claim_date_tools import calculate_timeline_duration, calculate_business_days, check_policy_compliance

llm = ChatOpenAI(model="gpt-3.5-turbo")
llm_with_tools = llm.bind_tools([
    calculate_timeline_duration,
    calculate_business_days,
    check_policy_compliance
])
```

---

## 🗄️ ChromaDB Integration

### Collections

The system uses two ChromaDB collections:

| Collection | Purpose | Chunking Method | Used By |
|------------|---------|-----------------|---------|
| `insurance_claims` | Smart semantic chunks | GPT-4o LLM | Summarization Expert |
| `small_chunks` | Hierarchical leaf nodes | LlamaIndex parser | Specific Task Expert |

### Configuration

```python
import chromadb

# Persistent client (saves to ./chroma_db)
client = chromadb.PersistentClient(path="./chroma_db")

# Create collection with OpenAI embeddings
from chromadb.utils import embedding_functions

openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

collection = client.get_or_create_collection(
    name="insurance_claims",
    embedding_function=openai_ef
)
```

### Querying

```python
# Vector similarity search
query_embedding = embeddings.embed_query("What is the claim amount?")

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
    include=["documents", "metadatas", "distances"]
)
```

---

## 🦙 LlamaIndex Integration

### HierarchicalNodeParser

Creates a 3-level hierarchy from documents:

```python
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes

node_parser = HierarchicalNodeParser.from_defaults(
    chunk_sizes=[2048, 512, 128]  # Root, Mid, Leaf
)

nodes = node_parser.get_nodes_from_documents(documents)
leaf_nodes = get_leaf_nodes(nodes)
```

### AutoMergingRetriever

Automatically merges child nodes when multiple match:

```python
from llama_index.core.retrievers import AutoMergingRetriever

# Build index over leaf nodes only
index = VectorStoreIndex(leaf_nodes, storage_context=storage_context)

# Create auto-merging retriever
retriever = AutoMergingRetriever(
    index.as_retriever(similarity_top_k=6),
    storage_context,
    verbose=True
)

# Query returns merged nodes when appropriate
nodes = retriever.retrieve("What happened during the incident?")
```

### Integration with ChromaDB

```python
from llama_index.vector_stores.chroma import ChromaVectorStore

vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

storage_context = StorageContext.from_defaults(
    docstore=SimpleDocumentStore(),
    vector_store=vector_store
)
```

---

## 📁 Project Structure

```
mid_assignment/
├── orchestrator_agent.py          # Main orchestrator - routes questions
├── summarization_expert_agent.py  # Broad questions expert
├── specific_task_expert_agent.py  # Specific questions expert
│
├── chromadb_chunk_pdf.py          # Smart LLM chunking + ChromaDB storage
├── hierarchical_retriever.py      # LlamaIndex hierarchical indexing
├── extract_claim_metadata.py      # Metadata extraction from PDFs
│
├── mcp/
│   ├── __init__.py
│   └── claim_date_tools.py        # MCP date/time calculation tools
│
├── chroma_db/                     # ChromaDB persistent storage
│   ├── chroma.sqlite3
│   └── docstore/
│       └── docstore.json          # LlamaIndex docstore
│
├── demo_chunking_comparison.py    # Naive vs smart chunking demo
├── demo_mcp_tools.py              # MCP tools demonstration
│
├── tests/
│   └── test_mcp_tools.py          # MCP tools unit tests
├── test_agents.py                 # Agent integration tests
├── test_hierarchical_retriever.py # Retriever tests
│
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables (not in repo)
└── README.md                      # This file
```

---

## 📚 API Reference

### OrchestratorAgent

```python
class OrchestratorAgent:
    def __init__(self, model_name="gpt-3.5-turbo")
    def classify_question(self, user_input: str) -> Tuple[int, str]
    def run(self, message: str) -> str
    def run_interactive(self)
```

### SpecificTaskExpertAgent

```python
class SpecificTaskExpertAgent:
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0, use_hierarchical_retrieval=True)
    def process_specific_question(self, user_input: str, context: Optional[str] = None) -> str
    def find_exact_value(self, query: str, data: str) -> str
    def locate_information(self, search_term: str, location_context: str) -> str
```

### SummarizationExpertAgent

```python
class SummarizationExpertAgent:
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.7, 
                 collection_name="insurance_claims", chroma_persist_dir="./chroma_db")
    def process_broad_question(self, user_input: str, context: Optional[str] = None) -> str
    def generate_summary(self, content: str, summary_type: str = "general") -> str
    def analyze_timeline(self, events: str) -> str
```

### HierarchicalClaimRetriever

```python
class HierarchicalClaimRetriever:
    def __init__(self, pdf_path: str, collection_name: str = "small_chunks",
                 chunk_sizes: Optional[list] = None, use_chromadb: bool = True)
    def load_pdf(self) -> list[Document]
    def build_hierarchy(self, documents: list[Document]) -> tuple
    def build_all(self, force_rebuild: bool = False) -> AutoMergingRetriever

# Convenience function
def get_claim_retriever(rebuild: bool = False, pdf_path: str = "insurance_claim_case.pdf",
                        use_chromadb: bool = True) -> AutoMergingRetriever
```

---

## 🧪 Testing

Run the test suite:

```bash
# All tests
python -m pytest

# Specific test files
python test_agents.py
python test_hierarchical_retriever.py
python tests/test_mcp_tools.py
```

---

## 📄 License

This project is part of an AI course assignment.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## 📧 Contact

For questions or support regarding this project, please open an issue on the repository.
