"""
Needle Agent - ReAct Agent with MCP Date/Time Tools for Insurance Claims.

This module demonstrates the integration of MCP date/time calculation tools
with a LangChain ReAct agent for insurance claim analysis.

The agent can:
- Calculate precise durations between timestamps
- Calculate business days excluding weekends
- Check policy compliance against deadlines
- Answer complex questions using reasoning and tools
"""

import os
import sys
from typing import List

# Add parent directories to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool

from mcp.claim_date_tools import (
    calculate_timeline_duration,
    calculate_business_days,
    check_policy_compliance
)


class NeedleAgent:
    """
    A ReAct agent specialized in insurance claim date/time analysis.
    
    This agent uses the ReAct (Reasoning and Acting) pattern to:
    1. Reason about which tool to use
    2. Act by invoking the appropriate tool
    3. Observe the result
    4. Repeat until the task is complete
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", verbose: bool = True):
        """
        Initialize the Needle Agent with MCP date/time tools.
        
        Args:
            model_name: The OpenAI model to use (default: gpt-3.5-turbo)
            verbose: Whether to show detailed agent reasoning (default: True)
        """
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.verbose = verbose
        
        # Initialize tools
        self.tools: List[BaseTool] = [
            calculate_timeline_duration,
            calculate_business_days,
            check_policy_compliance
        ]
        
        # Create ReAct prompt template
        self.prompt = self._create_react_prompt()
        
        # Create the ReAct agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=self.verbose,
            handle_parsing_errors=True,
            max_iterations=10
        )
    
    def _create_react_prompt(self) -> PromptTemplate:
        """
        Create a ReAct prompt template optimized for insurance claim analysis.
        
        Returns:
            PromptTemplate configured for the ReAct agent
        """
        template = """You are an expert insurance claim analyst assistant with access to specialized date/time calculation tools.

Your goal is to help analyze insurance claims by answering questions about timelines, deadlines, and policy compliance.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (must be a valid JSON object with the required parameters)
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT GUIDELINES:
1. Always parse dates carefully from the user's question
2. Use the correct date/datetime format for each tool (check tool descriptions)
3. When the user asks about "how long", "duration", or "time between", use calculate_timeline_duration
4. When the user asks about "business days", "working days", or "excluding weekends", use calculate_business_days
5. When the user asks about "deadline", "compliance", or "within X days", use check_policy_compliance
6. Provide clear, helpful answers based on the tool results
7. If dates are ambiguous, make reasonable assumptions and state them clearly

Begin!

Question: {input}
Thought: {agent_scratchpad}"""
        
        return PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools]),
                "tool_names": ", ".join([tool.name for tool in self.tools])
            }
        )
    
    def query(self, question: str) -> str:
        """
        Query the agent with a question about insurance claim dates/timelines.
        
        Args:
            question: The question to ask the agent
            
        Returns:
            The agent's answer
        """
        try:
            result = self.agent_executor.invoke({"input": question})
            return result.get("output", "No response generated")
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def list_available_tools(self) -> None:
        """Print information about available tools."""
        print("\n" + "=" * 70)
        print("AVAILABLE MCP TOOLS")
        print("=" * 70)
        for i, tool in enumerate(self.tools, 1):
            print(f"\n{i}. {tool.name}")
            print(f"   Description: {tool.description}")
        print("=" * 70 + "\n")


def demonstrate_standalone_tools():
    """Demonstrate standalone tool usage without the agent."""
    print("\n" + "=" * 70)
    print("DEMONSTRATION 1: STANDALONE TOOL TESTING")
    print("=" * 70)
    
    print("\n📊 Test 1: Calculate Timeline Duration")
    print("-" * 70)
    result = calculate_timeline_duration.invoke({
        "start_datetime": "2024-01-15 09:00:00",
        "end_datetime": "2024-01-18 14:30:00"
    })
    print(f"Result: {result}")
    
    print("\n📊 Test 2: Calculate Business Days")
    print("-" * 70)
    result = calculate_business_days.invoke({
        "start_date": "2024-01-15",
        "end_date": "2024-01-25"
    })
    print(f"Result: {result}")
    
    print("\n📊 Test 3: Check Policy Compliance (Compliant)")
    print("-" * 70)
    result = check_policy_compliance.invoke({
        "event_date": "2024-01-20",
        "reference_date": "2024-01-15",
        "deadline_days": 30
    })
    print(f"Result: {result}")
    
    print("\n📊 Test 4: Check Policy Compliance (Non-Compliant)")
    print("-" * 70)
    result = check_policy_compliance.invoke({
        "event_date": "2024-03-01",
        "reference_date": "2024-01-15",
        "deadline_days": 30
    })
    print(f"Result: {result}")
    
    print("\n" + "=" * 70)


def demonstrate_agent_with_tools():
    """Demonstrate the ReAct agent answering questions using tools."""
    print("\n" + "=" * 70)
    print("DEMONSTRATION 2: REACT AGENT WITH TOOLS")
    print("=" * 70)
    
    # Initialize agent
    agent = NeedleAgent(verbose=True)
    
    # Show available tools
    agent.list_available_tools()
    
    # Test questions
    questions = [
        "How long was the claim processing from 2024-01-15 09:00:00 to 2024-01-20 17:30:00?",
        "How many business days are there between January 15, 2024 and January 30, 2024?",
        "Was a claim filed on February 10, 2024 compliant if the incident occurred on January 15, 2024 and the policy requires filing within 30 days?",
        "A claim was reported on 2024-02-25. The incident happened on 2024-01-10. Is this within the 45-day reporting requirement?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'=' * 70}")
        print(f"QUESTION {i}: {question}")
        print(f"{'=' * 70}\n")
        
        answer = agent.query(question)
        
        print(f"\n{'─' * 70}")
        print(f"FINAL ANSWER:")
        print(f"{'─' * 70}")
        print(answer)
        print(f"{'=' * 70}\n")


def demonstrate_verbose_output():
    """Demonstrate verbose output showing tool selection reasoning."""
    print("\n" + "=" * 70)
    print("DEMONSTRATION 3: VERBOSE OUTPUT - AGENT REASONING")
    print("=" * 70)
    print("\nThis demonstrates how the agent reasons about which tool to use.")
    print("Watch for: Thought → Action → Action Input → Observation → Final Answer\n")
    
    agent = NeedleAgent(verbose=True)
    
    complex_question = """
    An insurance claim was filed on January 25, 2024 at 14:30:00.
    The incident occurred on January 10, 2024 at 08:00:00.
    The policy requires claims to be filed within 30 days.
    
    Please analyze:
    1. How much time elapsed from incident to filing?
    2. How many business days were used?
    3. Is this compliant with the policy?
    """
    
    print(f"COMPLEX QUESTION:\n{complex_question}\n")
    print("=" * 70)
    print("AGENT REASONING AND EXECUTION:\n")
    
    answer = agent.query(complex_question)
    
    print(f"\n{'=' * 70}")
    print("FINAL COMPREHENSIVE ANSWER:")
    print(f"{'=' * 70}")
    print(answer)


def interactive_mode():
    """Run the agent in interactive mode."""
    print("\n" + "=" * 70)
    print("INTERACTIVE MODE - NEEDLE AGENT")
    print("=" * 70)
    print("\nAsk questions about insurance claim dates and timelines!")
    print("Examples:")
    print("  - 'How long between Jan 15 9am and Jan 20 5pm?'")
    print("  - 'Business days from 2024-01-15 to 2024-01-30?'")
    print("  - 'Is filing on Feb 10 compliant if incident was Jan 15 with 30-day deadline?'")
    print("\nCommands: 'tools' to list tools, 'exit' or 'quit' to stop\n")
    
    agent = NeedleAgent(verbose=False)  # Less verbose for interactive mode
    
    while True:
        try:
            user_input = input("\n💼 Your Question: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'tools':
                agent.list_available_tools()
                continue
            
            if not user_input:
                continue
            
            print("\n🤔 Analyzing...")
            answer = agent.query(user_input)
            print(f"\n✅ Answer: {answer}")
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


def main():
    """Main function to run all demonstrations."""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "NEEDLE AGENT - MCP TOOLS DEMONSTRATION" + " " * 15 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'  (Linux/Mac)")
        print("  set OPENAI_API_KEY=your-api-key-here      (Windows CMD)")
        print("  $env:OPENAI_API_KEY='your-api-key-here'   (PowerShell)")
        api_key = input("\nEnter your OpenAI API key (or press Enter to skip demos): ").strip()
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        else:
            print("\n⚠️ Skipping demonstrations that require API access.\n")
            return
    
    try:
        # Run demonstrations
        print("\nChoose a demonstration mode:")
        print("  1. Standalone tool testing (no API calls)")
        print("  2. ReAct agent with tools (uses OpenAI API)")
        print("  3. Verbose output showing reasoning (uses OpenAI API)")
        print("  4. Interactive mode (uses OpenAI API)")
        print("  5. Run all demonstrations")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            demonstrate_standalone_tools()
        elif choice == "2":
            demonstrate_agent_with_tools()
        elif choice == "3":
            demonstrate_verbose_output()
        elif choice == "4":
            interactive_mode()
        elif choice == "5":
            demonstrate_standalone_tools()
            input("\nPress Enter to continue to next demonstration...")
            demonstrate_agent_with_tools()
            input("\nPress Enter to continue to next demonstration...")
            demonstrate_verbose_output()
            print("\n✅ All demonstrations completed!")
        else:
            print("Invalid choice. Running standalone tools demonstration.")
            demonstrate_standalone_tools()
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
