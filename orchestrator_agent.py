"""
Orchestrator Agent using LangChain
Classifies user questions into: 1) Needle in haystack, 2) Broad questions, 3) Other
Routes type 1 questions to Specific Task Expert agent.
Routes type 2 questions to the Summarization Expert agent.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Tuple
import os
from summarization_expert_agent import SummarizationExpertAgent
from specific_task_expert_agent import SpecificTaskExpertAgent


class OrchestratorAgent:
    """
    An orchestrator agent that classifies user questions.
    """
    
    def __init__(self, model_name="gpt-3.5-turbo"):
        """
        Initialize the orchestrator agent.
        
        Args:
            model_name: The LLM model to use
        """
        # Use temperature=0 for consistent classification
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        # Initialize the Summarization Expert agent for type 2 questions
        self.summarization_expert = SummarizationExpertAgent(model_name=model_name)
        # Initialize the Specific Task Expert agent for type 1 questions
        self.specific_task_expert = SpecificTaskExpertAgent(model_name=model_name)
        
    def classify_question(self, user_input: str) -> Tuple[int, str]:
        """
        Classify the user question into one of three types.
        
        Args:
            user_input: The user's question
            
        Returns:
            Tuple of (classification_number, explanation)
            - 1: Needle in haystack (specific, precise questions)
            - 2: Broad questions (summaries, timelines, high-level)
            - 3: Neither category 1 nor 2
        """
        try:
            classification_prompt = """You are a question classifier. Analyze the following user question and classify it into ONE of these categories:

**Category 1 - Needle in a Haystack (Specific Questions):**
- Very specific, precise questions requiring exact information
- Looking for particular facts, numbers, dates, or specific details
- Examples: 
  * "What was the exact error code in line 45?"
  * "Who approved the PR on March 5th?"
  * "What's the value of variable X in function Y?"
  * "Find the specific commit that introduced bug Z"

**Category 2 - Broad Questions (High-Level/Timeline-Oriented):**
- Summary requests, overviews, or general understanding
- Timeline-oriented questions spanning periods of time
- Examples:
  * "Summarize this issue"
  * "What happened last week?"
  * "Give me an overview of the project"
  * "What's the status of all open tickets?"
  * "Explain the overall architecture"

**Category 3 - Other:**
- Questions that don't fit categories 1 or 2
- General conversation, greetings, commands, calculations
- Examples:
  * "Hello", "Help", "Thank you"
  * "Calculate 2+2"
  * "Exit"

Respond with ONLY a number (1, 2, or 3) followed by a brief explanation.
Format: "NUMBER: explanation"

User Question: {question}

Your Classification:"""

            messages = [
                SystemMessage(content="You are a precise question classifier. Only respond with the format 'NUMBER: explanation'."),
                HumanMessage(content=classification_prompt.format(question=user_input))
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # Extract the number from the response
            if response_text.startswith('1'):
                classification = 1
            elif response_text.startswith('2'):
                classification = 2
            elif response_text.startswith('3'):
                classification = 3
            else:
                # Default to 3 if unclear
                classification = 3
                response_text = "3: Unable to clearly classify the question"
            
            # Extract explanation (everything after the number and colon)
            explanation = response_text.split(':', 1)[1].strip() if ':' in response_text else response_text
            
            return classification, explanation
            
        except Exception as e:
            return 3, f"Error in classification: {str(e)}"
    
    def run(self, message: str) -> str:
        """
        Process user message, classify it, and route to appropriate handler.
        Type 1 questions are sent to the Specific Task Expert agent.
        Type 2 questions are sent to the Summarization Expert agent.
        
        Args:
            message: The user's question
            
        Returns:
            Formatted classification result and response
        """
        try:
            # Classify the question
            classification, explanation = self.classify_question(message)
            
            classification_labels = {
                1: "🔍 Type 1: Needle in Haystack (Specific Question)",
                2: "📊 Type 2: Broad Question (Summary/Timeline)",
                3: "💬 Type 3: Other Question Type"
            }
            
            result = f"""
╔══════════════════════════════════════════════════════════╗
║ QUESTION CLASSIFICATION RESULT                           ║
╠══════════════════════════════════════════════════════════╣
║ Classification: {classification}
║ Type: {classification_labels[classification]}
║ 
║ Explanation: {explanation}
╚══════════════════════════════════════════════════════════╝
"""
            
            # Route Type 1 questions to Specific Task Expert
            if classification == 1:
                result += "\n🔄 Routing to Specific Task Expert Agent...\n"
                result += "─" * 60 + "\n"
                
                # Send to Specific Task Expert agent
                expert_response = self.specific_task_expert.process_specific_question(message)
                
                result += "\n🎯 SPECIFIC TASK EXPERT RESPONSE:\n"
                result += "─" * 60 + "\n"
                result += expert_response
                result += "\n" + "─" * 60
            
            # Route Type 2 questions to Summarization Expert
            elif classification == 2:
                result += "\n� Routing to Summarization Expert Agent...\n"
                result += "─" * 60 + "\n"
                
                # Send to Summarization Expert agent
                expert_response = self.summarization_expert.process_broad_question(message)
                
                result += "\n📋 SUMMARIZATION EXPERT RESPONSE:\n"
                result += "─" * 60 + "\n"
                result += expert_response
                result += "\n" + "─" * 60
            
            else:
                result += "\n💡 This question doesn't require specialized handling."
            
            return result
            
        except Exception as e:
            return f"❌ Error running agent: {str(e)}"
    
    def run_interactive(self):
        """Run the agent in interactive terminal mode."""
        print("=" * 60)
        print("Orchestrator Agent - Question Classification Mode")
        print("=" * 60)
        print("This agent classifies your questions into:")
        print("  1️⃣  Needle in Haystack (Specific questions)")
        print("  2️⃣  Broad Questions (Summaries/Timelines)")
        print("  3️⃣  Other types")
        print("\nType your questions to see how they're classified!")
        print("Commands: 'exit', 'quit', or 'q' to stop\n")
        
        while True:
            try:
                user_input = input("\n🤖 You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 Shutting down orchestrator agent. Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("\n💭 Analyzing your question...")
                response = self.run(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted. Shutting down orchestrator agent.")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")


def main():
    """Main function to run the orchestrator agent."""
    print("🚀 Initializing Orchestrator Agent with Question Classification...\n")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
        print("Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'  (Linux/Mac)")
        print("  $env:OPENAI_API_KEY='your-api-key-here'   (PowerShell)")
        api_key = input("\nEnter your OpenAI API key (or press Enter to skip): ").strip()
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        else:
            print("\n⚠️  Continuing without API key (will fail when making API calls)\n")
    
    try:
        agent = OrchestratorAgent()
        agent.run_interactive()
    except Exception as e:
        print(f"\n❌ Failed to initialize agent: {str(e)}")
        print("\nMake sure you have installed required packages:")
        print("  pip install langchain langchain-openai")


if __name__ == "__main__":
    main()
