# Orchestrator Agent with Summarization Expert

A multi-agent system built with LangChain that intelligently classifies user questions and routes them to specialized agents.

## 🏗️ Architecture

### Two-Agent System:

1. **Orchestrator Agent** (`orchestrator_agent.py`)
   - Classifies user questions into 3 types using LLM
   - Routes Type 2 questions to the Summarization Expert
   - Coordinates the overall workflow

2. **Summarization Expert Agent** (`summarization_expert_agent.py`)
   - Specialized in handling broad questions
   - Creates comprehensive summaries and overviews
   - Analyzes timelines and trends

## 📊 Question Classification

The Orchestrator classifies questions into:

### Type 1️⃣: Needle in Haystack (Specific Questions)
- Very precise questions requiring exact information
- Examples:
  - "What was the exact error code in line 45?"
  - "Who approved the PR on March 5th?"
  - "What's the value of variable X in function Y?"

### Type 2️⃣: Broad Questions (Summary/Timeline)
- Summary requests and overviews
- Timeline-oriented questions
- **Automatically routed to Summarization Expert Agent**
- Examples:
  - "Summarize this issue"
  - "What happened last week?"
  - "Give me an overview of the project"
  - "What's the status of all open tickets?"

### Type 3️⃣: Other
- Questions that don't fit Type 1 or 2
- General conversation, greetings, commands
- Examples:
  - "Hello", "Help", "Thank you"
  - "Calculate 2+2"

## 🚀 Installation

1. Install required packages:

```bash
pip install -r requirements.txt
```

2. Set up your OpenAI API key:

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY='your_api_key_here'
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY='your_api_key_here'
```

Or create a `.env` file:
```bash
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-3.5-turbo
TEMPERATURE=0.7
```

## 💻 Usage

### Interactive Mode

Run the orchestrator agent:

```bash
python orchestrator_agent.py
```

### Example Interaction

```
🤖 You: Summarize the key developments in AI this year

💭 Analyzing your question...

╔══════════════════════════════════════════════════════════╗
║ QUESTION CLASSIFICATION RESULT                           ║
╠══════════════════════════════════════════════════════════╣
║ Classification: 2
║ Type: 📊 Type 2: Broad Question (Summary/Timeline)
║ 
║ Explanation: This is a broad summary request...
╚══════════════════════════════════════════════════════════╝

🔄 Routing to Summarization Expert Agent...
────────────────────────────────────────────────────────────

📋 SUMMARIZATION EXPERT RESPONSE:
────────────────────────────────────────────────────────────
[Comprehensive summary from Summarization Expert]
────────────────────────────────────────────────────────────
```

### Programmatic Usage

```python
from orchestrator_agent import OrchestratorAgent

# Initialize
agent = OrchestratorAgent(model_name="gpt-3.5-turbo")

# Process a question
response = agent.run("Summarize the project status from last month")
print(response)
```

### Test the Agents

Run the test script to see all question types:

```bash
python test_agents.py
```

## 📁 Project Structure

```
mid_assignment/
├── orchestrator_agent.py          # Main orchestrator agent
├── summarization_expert_agent.py  # Specialized summarization agent
├── test_agents.py                 # Test script
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
└── README.md                      # This file
```

## 🔄 Workflow

1. **User Input** → Orchestrator Agent
2. **Classification** → LLM analyzes question type (1, 2, or 3)
3. **Routing Decision**:
   - **Type 2** → Summarization Expert Agent → Comprehensive Response
   - **Type 1** → (Reserved for future needle-in-haystack agent)
   - **Type 3** → Standard handling
4. **Response** → Formatted output to user

## 🎯 Features

### Orchestrator Agent
- ✅ Intelligent question classification using LLM
- ✅ Clear classification explanations
- ✅ Automatic routing to specialist agents
- ✅ Interactive terminal interface
- ✅ Formatted, user-friendly output

### Summarization Expert Agent
- ✅ Comprehensive summaries and overviews
- ✅ Timeline analysis capabilities
- ✅ Multiple summary types (general, timeline, executive, technical)
- ✅ Context-aware responses
- ✅ Specialized prompting for broad questions

## 🛠️ Advanced Usage

### Using Summarization Expert Directly

```python
from summarization_expert_agent import SummarizationExpertAgent

agent = SummarizationExpertAgent()

# Process broad question
response = agent.process_broad_question("Summarize this issue")

# Generate specific summary types
summary = agent.generate_summary(content, summary_type="timeline")

# Analyze timeline
timeline = agent.analyze_timeline(events)

# Get overview
overview = agent.get_overview("Project Architecture")
```

## 🔧 Configuration

Customize the agents by passing parameters:

```python
# Orchestrator with custom model
orchestrator = OrchestratorAgent(model_name="gpt-4")

# Summarization Expert with custom settings
expert = SummarizationExpertAgent(
    model_name="gpt-4",
    temperature=0.7  # More creative summaries
)
```

## 📝 Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for API calls

## 🔐 Security Notes

- Never commit your `.env` file or expose API keys
- Use `.env.example` as a template only
- Add `.env` to your `.gitignore`
- Revoke any exposed API keys immediately

## 🎓 Example Use Cases

1. **Project Management**: "Summarize all tickets closed last sprint"
2. **Code Review**: "Give me an overview of changes in the feature branch"
3. **Documentation**: "What are the key components of this system?"
4. **Timeline Analysis**: "What happened in the development process last quarter?"

## 🚧 Future Enhancements

- [ ] Implement Needle-in-Haystack search agent for Type 1 questions
- [ ] Add RAG (Retrieval Augmented Generation) for context
- [ ] Support for document/code base indexing
- [ ] Multi-turn conversations with memory
- [ ] Export summaries to different formats

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Feel free to submit issues or pull requests.
