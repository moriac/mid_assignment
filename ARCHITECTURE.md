# Agent System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                              │
│                    (Terminal Message)                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR AGENT                            │
│                  (orchestrator_agent.py)                        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐      │
│  │  LLM-Based Question Classification                   │      │
│  │  - Analyzes user question                            │      │
│  │  - Returns classification (1, 2, or 3)               │      │
│  │  - Provides explanation                              │      │
│  └──────────────────────────────────────────────────────┘      │
└──────────────────┬───────────────┬──────────────┬───────────────┘
                   │               │              │
         ┌─────────▼────┐  ┌──────▼─────┐  ┌────▼──────┐
         │   Type 1     │  │  Type 2    │  │  Type 3   │
         │ Needle in    │  │   Broad    │  │   Other   │
         │  Haystack    │  │  Question  │  │           │
         └─────────┬────┘  └──────┬─────┘  └────┬──────┘
                   │               │              │
                   ▼               ▼              │
    ┌──────────────────────┐ ┌─────────────────────┐
    │ SPECIFIC TASK        │ │ SUMMARIZATION       │
    │ EXPERT AGENT         │ │ EXPERT AGENT        │
    │(specific_task_       │ │(summarization_      │
    │ expert_agent.py)     │ │ expert_agent.py)    │
    │                      │ │                     │
    │ • Precise answers    │ │ • Comprehensive     │
    │ • Exact information  │ │   summaries         │
    │ • Specific details   │ │ • Timeline analysis │
    │ • Needle-in-haystack │ │ • High-level        │
    │   searches           │ │   overviews         │
    └──────────┬───────────┘ └──────────┬──────────┘
               │                        │
               ▼                        ▼
         ┌──────────────────────────────────────────────┐
         │        FORMATTED RESPONSE TO USER            │
         │   • Classification details                   │
         │   • Expert agent response                    │
         │   • Status message                           │
         └──────────────────────────────────────────────┘
```

## Data Flow

1. **User Input** → Question entered in terminal
2. **Classification** → Orchestrator uses LLM to classify (Type 1, 2, or 3)
3. **Routing**:
   - **Type 1** → Sent to Specific Task Expert Agent
   - **Type 2** → Sent to Summarization Expert Agent
   - **Type 3** → Basic handling
4. **Processing** → Appropriate agent processes the question
5. **Response** → Formatted output returned to user

## Classification Logic

```python
Type 1: Specific Questions ⟶ [Specific Task Expert]
├── Exact information requests
├── Precise facts/numbers/dates
└── Example: "What was the error code in line 45?"

Type 2: Broad Questions ⟶ [Summarization Expert]
├── Summary requests
├── Timeline-oriented questions
├── Overview requests
└── Example: "Summarize last month's activities"

Type 3: Other
├── General conversation
├── Commands/calculations
└── Example: "Hello", "Calculate 2+2"
```

## Agent Responsibilities

### Orchestrator Agent
- ✓ Question classification using LLM
- ✓ Routing logic to appropriate expert
- ✓ User interaction management
- ✓ Response formatting

### Specific Task Expert Agent (Type 1)
- ✓ Precise, exact answers
- ✓ Needle-in-haystack searches
- ✓ Specific detail extraction
- ✓ Location-based information retrieval
- ✓ Temperature = 0 for consistency

### Summarization Expert Agent (Type 2)
- ✓ Comprehensive summaries
- ✓ Timeline analysis
- ✓ High-level overviews
- ✓ Broad question handling
- ✓ Temperature = 0.7 for creative summaries
