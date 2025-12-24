# MCP Tools Quick Start Guide

## 🚀 Quick Installation

```bash
# Navigate to project directory
cd c:\Dev\AI_Course\mid_assignment

# Install required packages (if not already installed)
pip install langchain langchain-openai
```

## ⚡ Quick Test (No API Key Required)

Test the core calculation logic:

```bash
python test_core_logic.py
```

Expected output: ✅ ALL TESTS PASSED!

## 📊 See Tools in Action

Run demonstrations:

```bash
python demo_mcp_tools.py
```

This shows 7 practical examples of insurance claim analysis.

## 🧪 Run Full Test Suite

If you have LangChain installed:

```bash
python tests\test_mcp_tools.py
```

Expected: 50 tests, all passing

## 🤖 Try the ReAct Agent (Requires OpenAI API Key)

```bash
# Set your API key
set OPENAI_API_KEY=sk-your-key-here

# Run the agent demo
python src\agents\needle_agent.py

# Choose option 1 for standalone tools (no API)
# Choose option 2-4 for agent demonstrations (uses API)
```

## 💻 Use in Your Code

### Standalone Tool Usage

```python
from mcp.claim_date_tools import calculate_timeline_duration

# Calculate duration
result = calculate_timeline_duration.invoke({
    "start_datetime": "2024-01-15 09:00:00",
    "end_datetime": "2024-01-20 17:30:00"
})
print(result)
# Output: Duration: 5 days, 8 hours, 30 minutes (Total: 128.50 hours)
```

### With Your Agent

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from mcp.claim_date_tools import (
    calculate_timeline_duration,
    calculate_business_days,
    check_policy_compliance
)

# Initialize
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
tools = [calculate_timeline_duration, calculate_business_days, check_policy_compliance]

# Create agent with your prompt template
agent = create_react_agent(llm=llm, tools=tools, prompt=your_prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Query
result = executor.invoke({"input": "How many business days from Jan 15 to Jan 30?"})
```

## 📁 File Locations

- **Tools**: `mcp/claim_date_tools.py`
- **Tests**: `tests/test_mcp_tools.py`
- **Agent Example**: `src/agents/needle_agent.py`
- **Full Docs**: `MCP_TOOLS_README.md`

## 🎯 Common Use Cases

### 1. Calculate Processing Time
```python
calculate_timeline_duration.invoke({
    "start_datetime": "2024-01-15 09:00:00",
    "end_datetime": "2024-01-20 17:30:00"
})
```

### 2. Check SLA Compliance
```python
calculate_business_days.invoke({
    "start_date": "2024-01-15",
    "end_date": "2024-01-30"
})
```

### 3. Verify Filing Deadline
```python
check_policy_compliance.invoke({
    "event_date": "2024-01-25",
    "reference_date": "2024-01-10",
    "deadline_days": 30
})
```

## ❓ Troubleshooting

**"ModuleNotFoundError: No module named 'langchain'"**
```bash
pip install langchain langchain-openai
```

**"OPENAI_API_KEY not found"** (for agent demos only)
```bash
set OPENAI_API_KEY=sk-your-key-here
```

**Import errors**
```bash
# Make sure you're in the project root
cd c:\Dev\AI_Course\mid_assignment
python -c "from mcp.claim_date_tools import calculate_timeline_duration; print('OK')"
```

## 📚 Next Steps

1. ✅ Run `test_core_logic.py` to verify installation
2. ✅ Run `demo_mcp_tools.py` to see examples
3. ✅ Read `MCP_TOOLS_README.md` for full documentation
4. ✅ Try `needle_agent.py` for agent integration

## 🎓 Integration Examples

The tools are already integrated into:
- `orchestrator_agent.py` - Main orchestrator
- `specific_task_expert_agent.py` - Task expert

Access them via:
```python
from orchestrator_agent import OrchestratorAgent

agent = OrchestratorAgent()
# Tools available in agent.date_tools
```

---

**Need Help?** Check `MCP_TOOLS_README.md` for comprehensive documentation.
