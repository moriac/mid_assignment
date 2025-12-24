# MCP Date/Time Tools for Insurance Claim Analysis

## Overview

This implementation provides **Model Context Protocol (MCP)** date/time calculation tools specifically designed for insurance claim analysis using LangChain's `@tool` decorator. These tools enable LangChain ReAct agents to perform precise date/time calculations for compliance checking, timeline analysis, and business day calculations.

## 🎯 Features

- **Three specialized MCP tools** for insurance claim date/time analysis
- **LangChain integration** using `@tool` decorator for seamless agent compatibility
- **Comprehensive error handling** with helpful error messages
- **Pure functions** with no side effects or external state dependencies
- **Full test coverage** with 50+ unit tests including edge cases
- **ReAct agent example** demonstrating tool selection and reasoning

## 📁 Project Structure

```
mid_assignment/
├── mcp/
│   ├── __init__.py
│   └── claim_date_tools.py          # MCP tool implementations
├── src/
│   └── agents/
│       ├── __init__.py
│       └── needle_agent.py          # ReAct agent integration example
├── tests/
│   ├── __init__.py
│   └── test_mcp_tools.py            # Comprehensive unit tests
├── orchestrator_agent.py            # Integrated with date tools
└── specific_task_expert_agent.py    # Integrated with date tools
```

## 🛠️ Tools Description

### 1. `calculate_timeline_duration`

Calculates precise duration between two timestamps.

**Signature:**
```python
calculate_timeline_duration(start_datetime: str, end_datetime: str) -> str
```

**Input Format:**
- `start_datetime`: "YYYY-MM-DD HH:MM:SS" (e.g., "2024-01-15 09:00:00")
- `end_datetime`: "YYYY-MM-DD HH:MM:SS" (e.g., "2024-01-18 14:30:00")

**Returns:**
```
"Duration: 3 days, 5 hours, 30 minutes (Total: 77.50 hours)"
```

**When to use:**
- User asks: "how long", "duration", "time between", "elapsed time"
- Timeline analysis questions
- Incident to report time calculations

**Example:**
```python
from mcp.claim_date_tools import calculate_timeline_duration

result = calculate_timeline_duration.invoke({
    "start_datetime": "2024-01-15 09:00:00",
    "end_datetime": "2024-01-18 14:30:00"
})
print(result)
# Output: Duration: 3 days, 5 hours, 30 minutes (Total: 77.50 hours)
```

---

### 2. `calculate_business_days`

Calculates business days (Monday-Friday) between two dates, excluding weekends.

**Signature:**
```python
calculate_business_days(start_date: str, end_date: str) -> str
```

**Input Format:**
- `start_date`: "YYYY-MM-DD" (e.g., "2024-01-15")
- `end_date`: "YYYY-MM-DD" (e.g., "2024-01-25")

**Returns:**
```
"Business days: 8, Calendar days: 10, Weekend days: 2 (from 2024-01-15 to 2024-01-25)"
```

**When to use:**
- User asks: "business days", "working days", "weekdays", "excluding weekends"
- Turnaround time calculations
- Processing time analysis

**Example:**
```python
from mcp.claim_date_tools import calculate_business_days

result = calculate_business_days.invoke({
    "start_date": "2024-01-15",
    "end_date": "2024-01-25"
})
print(result)
# Output: Business days: 8, Calendar days: 10, Weekend days: 2 (from 2024-01-15 to 2024-01-25)
```

---

### 3. `check_policy_compliance`

Checks if an event occurred within required policy timeframe.

**Signature:**
```python
check_policy_compliance(event_date: str, reference_date: str, deadline_days: int) -> str
```

**Input Format:**
- `event_date`: "YYYY-MM-DD" (e.g., "2024-01-20")
- `reference_date`: "YYYY-MM-DD" (e.g., "2024-01-15")
- `deadline_days`: integer (e.g., 30)

**Returns (Compliant):**
```
"COMPLIANT: Event occurred 5 days after reference date. Deadline: 30 days. Status: Within deadline (25 days remaining)"
```

**Returns (Non-Compliant):**
```
"NON-COMPLIANT: Event occurred 36 days after reference date. Deadline: 30 days. Status: EXCEEDED deadline by 6 days"
```

**When to use:**
- User asks: "check deadline", "verify compliance", "within timeframe"
- Policy requirement validation
- Filing deadline checks

**Example:**
```python
from mcp.claim_date_tools import check_policy_compliance

result = check_policy_compliance.invoke({
    "event_date": "2024-01-20",
    "reference_date": "2024-01-15",
    "deadline_days": 30
})
print(result)
# Output: COMPLIANT: Event occurred 5 days after reference date. Deadline: 30 days...
```

## 🚀 Installation & Setup

### 1. Install Dependencies

```bash
pip install langchain langchain-openai python-dotenv
```

### 2. Set OpenAI API Key

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=your-api-key-here
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY='your-api-key-here'
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

### 3. Verify Installation

```bash
# Run unit tests
python tests/test_mcp_tools.py

# Run standalone tool demo (no API needed)
python src/agents/needle_agent.py
# Choose option 1
```

## 📝 Usage Examples

### Standalone Tool Usage

```python
from mcp.claim_date_tools import (
    calculate_timeline_duration,
    calculate_business_days,
    check_policy_compliance
)

# Calculate duration
duration = calculate_timeline_duration.invoke({
    "start_datetime": "2024-01-15 09:00:00",
    "end_datetime": "2024-01-20 17:30:00"
})

# Calculate business days
biz_days = calculate_business_days.invoke({
    "start_date": "2024-01-15",
    "end_date": "2024-01-30"
})

# Check compliance
compliance = check_policy_compliance.invoke({
    "event_date": "2024-02-10",
    "reference_date": "2024-01-15",
    "deadline_days": 30
})
```

### ReAct Agent Integration

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from mcp.claim_date_tools import (
    calculate_timeline_duration,
    calculate_business_days,
    check_policy_compliance
)

# Initialize LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# Define tools
tools = [
    calculate_timeline_duration,
    calculate_business_days,
    check_policy_compliance
]

# Create ReAct agent (use appropriate prompt template)
agent = create_react_agent(llm=llm, tools=tools, prompt=your_prompt_template)

# Create executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

# Query agent
result = agent_executor.invoke({
    "input": "How many business days between Jan 15 and Jan 30, 2024?"
})
print(result["output"])
```

### Using the Needle Agent

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.needle_agent import NeedleAgent

# Initialize agent
agent = NeedleAgent(verbose=True)

# Ask questions
answer = agent.query(
    "Was a claim filed on Feb 10, 2024 compliant if the incident "
    "occurred on Jan 15, 2024 with a 30-day filing requirement?"
)
print(answer)
```

## 🧪 Testing

### Run All Tests

```bash
python tests/test_mcp_tools.py
```

### Expected Output

```
test_business_days_including_two_weekends ... ok
test_compliant_on_last_day ... ok
test_end_before_start ... ok
test_invalid_event_date_format ... ok
test_month_boundary ... ok
test_same_datetime ... ok
...

----------------------------------------------------------------------
Ran 50 tests in 0.245s

OK

======================================================================
TEST SUMMARY
======================================================================
Tests Run: 50
Successes: 50
Failures: 0
Errors: 0
======================================================================
```

### Test Coverage

- ✅ **Correct calculations** - Duration, business days, compliance
- ✅ **Edge cases** - Same day, month/year boundaries, leap year
- ✅ **Error handling** - Invalid formats, missing data, logic errors
- ✅ **Boundary conditions** - Zero values, last-day deadlines

## 🎮 Demonstrations

### Run the Needle Agent Demos

```bash
cd c:\Dev\AI_Course\mid_assignment
python src/agents/needle_agent.py
```

**Available Demos:**
1. **Standalone tool testing** - Test tools without API calls
2. **ReAct agent with tools** - See agent select and use tools
3. **Verbose output** - Watch agent reasoning process
4. **Interactive mode** - Ask your own questions
5. **Run all** - Execute all demonstrations

### Example Agent Output

```
═══════════════════════════════════════════════════════════════════
QUESTION 1: How many business days between January 15 and 30, 2024?
═══════════════════════════════════════════════════════════════════

> Entering new AgentExecutor chain...
I need to calculate business days between two dates

Action: calculate_business_days
Action Input: {"start_date": "2024-01-15", "end_date": "2024-01-30"}
Observation: Business days: 11, Calendar days: 15, Weekend days: 4...

Thought: I now know the final answer
Final Answer: There are 11 business days between January 15 and 30, 2024...
```

## 🔧 Integration with Existing Agents

The tools have been integrated into:

### 1. Orchestrator Agent

File: `orchestrator_agent.py`

```python
from mcp.claim_date_tools import (
    calculate_timeline_duration,
    calculate_business_days,
    check_policy_compliance
)

class OrchestratorAgent:
    def __init__(self, model_name="gpt-3.5-turbo"):
        # ... existing code ...
        self.date_tools = [
            calculate_timeline_duration,
            calculate_business_days,
            check_policy_compliance
        ]
```

### 2. Specific Task Expert Agent

File: `specific_task_expert_agent.py`

```python
from mcp.claim_date_tools import (
    calculate_timeline_duration,
    calculate_business_days,
    check_policy_compliance
)

class SpecificTaskExpertAgent:
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0):
        # ... existing code ...
        self.date_tools = [
            calculate_timeline_duration,
            calculate_business_days,
            check_policy_compliance
        ]
```

## 🎯 Key Features

### LangChain-Specific Design

✅ **@tool decorator** - Native LangChain tool integration  
✅ **Comprehensive docstrings** - Help agents understand when to use tools  
✅ **Trigger phrases** - Keywords for agent tool selection  
✅ **String returns** - Optimal for LLM agent processing  
✅ **Error messages** - Agent-friendly error descriptions  

### Error Handling

All tools include robust error handling:

```python
# Invalid date format
>>> calculate_timeline_duration.invoke({
...     "start_datetime": "01/15/2024 09:00",
...     "end_datetime": "2024-01-20 17:00:00"
... })
"Error: Invalid start_datetime format '01/15/2024 09:00'. 
Required format: 'YYYY-MM-DD HH:MM:SS' (e.g., '2024-01-15 09:30:00')"

# End before start
>>> check_policy_compliance.invoke({
...     "event_date": "2024-01-10",
...     "reference_date": "2024-01-15",
...     "deadline_days": 30
... })
"INVALID: Event date (2024-01-10) is 5 days BEFORE reference date (2024-01-15). 
Event should occur after reference date."
```

### Type Safety

All functions use proper type hints:

```python
def calculate_timeline_duration(start_datetime: str, end_datetime: str) -> str:
    """..."""
    
def calculate_business_days(start_date: str, end_date: str) -> str:
    """..."""
    
def check_policy_compliance(event_date: str, reference_date: str, deadline_days: int) -> str:
    """..."""
```

## 📚 Documentation

Each tool includes:

1. **Clear description** - What the tool does
2. **When to use** - Example queries and keywords
3. **Parameter descriptions** - Exact formats required
4. **Return value description** - What to expect
5. **Example usage** - Code samples
6. **Trigger phrases** - Help agent understand tool selection

## 🐛 Troubleshooting

### Common Issues

**Issue: "OPENAI_API_KEY not found"**
```bash
# Set your API key
set OPENAI_API_KEY=sk-...
```

**Issue: "ModuleNotFoundError: No module named 'mcp'"**
```bash
# Run from project root
cd c:\Dev\AI_Course\mid_assignment
python tests/test_mcp_tools.py
```

**Issue: Agent not selecting correct tool**
- Check tool docstrings include relevant keywords
- Ensure verbose=True to see agent reasoning
- Verify prompt template is correct

## 🎓 Best Practices

1. **Always validate dates** - Use try/except for parsing
2. **Return strings** - LLM agents process text better than dicts
3. **Include context** - Return explanations with results
4. **Handle edge cases** - Same day, month boundaries, etc.
5. **Clear error messages** - Help agent understand what went wrong
6. **Use type hints** - Improve code clarity and IDE support

## 📄 License

This implementation is part of the AI Course mid-assignment project.

## 👥 Author

Created for insurance claim analysis automation using LangChain and MCP tools.

---

**Last Updated:** December 24, 2025
