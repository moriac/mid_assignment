# Quick Start Guide

## Setup (5 minutes)

### 1. Set Your API Key

**Option A: Environment Variable (Recommended)**
```powershell
# Windows PowerShell
$env:OPENAI_API_KEY='your-api-key-here'
```

**Option B: Create .env file**
```bash
# Create .env file
OPENAI_API_KEY=your-api-key-here
```

### 2. Run the Agent

```bash
python orchestrator_agent.py
```

## Try These Examples

Once the agent starts, try these questions:

### Type 1 Examples (Specific Questions)
```
🤖 You: What was the exact error code in line 45?
🤖 You: Who approved the PR on March 5th?
🤖 You: What's the value of variable X?
```
**Result**: Classified as Type 1 - Needle in Haystack

### Type 2 Examples (Broad Questions) → Routes to Summarization Expert
```
🤖 You: Summarize the key developments this year
🤖 You: What happened in the project last month?
🤖 You: Give me an overview of the system architecture
🤖 You: What's the timeline of events?
```
**Result**: Classified as Type 2 → Sent to Summarization Expert Agent

### Type 3 Examples (Other)
```
🤖 You: Hello
🤖 You: Calculate 25 * 4
🤖 You: Help
```
**Result**: Classified as Type 3 - Other

## Exit the Agent

Type any of these commands:
- `exit`
- `quit`
- `q`

Or press `Ctrl+C`

## Expected Output Format

```
╔══════════════════════════════════════════════════════════╗
║ QUESTION CLASSIFICATION RESULT                           ║
╠══════════════════════════════════════════════════════════╣
║ Classification: 2
║ Type: 📊 Type 2: Broad Question (Summary/Timeline)
║ 
║ Explanation: This is a summary request requiring...
╚══════════════════════════════════════════════════════════╝

🔄 Routing to Summarization Expert Agent...
────────────────────────────────────────────────────────────

📋 SUMMARIZATION EXPERT RESPONSE:
────────────────────────────────────────────────────────────
[Detailed summary from the expert agent]
────────────────────────────────────────────────────────────
```

## Troubleshooting

### Issue: "OPENAI_API_KEY not found"
**Solution**: Set your API key using one of the methods in step 1

### Issue: Import errors
**Solution**: Install dependencies
```bash
pip install langchain langchain-openai
```

### Issue: Agent not responding
**Solution**: Check your internet connection and API key validity

## Testing Multiple Questions

Run the test script:
```bash
python test_agents.py
```

This will test all three question types automatically.

## What's Happening Behind the Scenes?

1. ✅ Your question is sent to the **Orchestrator Agent**
2. ✅ The Orchestrator uses **LLM to classify** your question (1, 2, or 3)
3. ✅ If Type 2, it's **automatically routed** to the **Summarization Expert Agent**
4. ✅ The expert agent generates a **comprehensive response**
5. ✅ You receive a **formatted output** with classification + response

## Next Steps

- Try different types of questions
- Observe how the classification works
- See the Summarization Expert in action for broad questions
- Read ARCHITECTURE.md for detailed system design
