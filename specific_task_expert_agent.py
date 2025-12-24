"""
Specific Task Expert Agent using LangChain
Handles Type 1 questions: "Needle in Haystack" - specific, precise questions.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from typing import Optional
import os
from supabase_utils import get_top_k_chunks_from_small_chunks
from mcp.claim_date_tools import (
    calculate_timeline_duration,
    calculate_business_days,
    check_policy_compliance
)


class SpecificTaskExpertAgent:
    """
    A specialized agent for handling specific, precise "needle in haystack" questions.
    This agent excels at finding exact information and providing precise answers.
    """
    
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0):
        """
        Initialize the Specific Task Expert agent.
        
        Args:
            model_name: The LLM model to use
            temperature: Temperature set to 0 for precise, consistent answers
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        # Initialize MCP date/time tools
        self.date_tools = [
            calculate_timeline_duration,
            calculate_business_days,
            check_policy_compliance
        ]
        # Bind tools to LLM for automatic tool calling
        self.llm_with_tools = self.llm.bind_tools(self.date_tools)
        
    def process_specific_question(self, user_input: str, context: Optional[str] = None) -> str:
        """
        Process a specific "needle in haystack" question and provide a precise answer.
        
        Args:
            user_input: The user's specific question
            context: Optional context or data to search within
            
        Returns:
            A precise, specific answer
        """
        try:
            # Retrieve top 3 relevant chunks from Supabase
            relevant_chunks = get_top_k_chunks_from_small_chunks(user_input, k=3)
            context_str = "\n---\n".join(relevant_chunks) if relevant_chunks else None

            system_prompt = """You are an Insurance representative expert that answers specific questions with precision and accuracy. You are a specialized assistant specializing in:
- Finding exact information (needle in haystack)
- Providing precise, accurate answers
- Locating specific facts, numbers, dates, and details
- Answering targeted questions with exactness
- Identifying specific values, codes, names, or references

Your responses should be:
1. Precise and exact - no unnecessary elaboration
2. Factual and accurate
3. Direct and to the point
4. Include specific references when possible (line numbers, dates, names, etc.)
5. Acknowledge if the specific information is not available

You have access to the following MCP tools for date/time calculations:
- calculate_timeline_duration: Calculate time between two dates
- calculate_business_days: Calculate business days between dates
- check_policy_compliance: Check if dates meet policy deadlines

Use these tools when the question involves date/time calculations or compliance checks.

Focus on providing the exact answer to the specific question asked."""

            # Build the user message
            user_message = f"User Question: {user_input}"
            if context_str:
                user_message += f"\n\nContext/Data to search:\n{context_str}"
            user_message += "\n\nPlease provide a precise, specific answer to this question."

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]

            # Invoke the LLM with tools
            print("\n🔧 Available MCP Tools: calculate_timeline_duration, calculate_business_days, check_policy_compliance")
            response = self.llm_with_tools.invoke(messages)
            
            # Check if tools were used
            tool_calls = []
            if hasattr(response, 'tool_calls') and response.tool_calls:
                tool_calls = response.tool_calls
                print(f"\n🔧 MCP TOOLS USED: {len(tool_calls)} tool(s) called")
                for tool_call in tool_calls:
                    print(f"   ├─ Tool: {tool_call['name']}")
                    print(f"   └─ Args: {tool_call['args']}")
                
                # Execute tool calls and get results
                messages.append(response)
                for tool_call in tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    
                    # Find and invoke the tool
                    tool_result = None
                    for tool in self.date_tools:
                        if tool.name == tool_name:
                            tool_result = tool.invoke(tool_args)
                            print(f"   ✅ {tool_name} result: {tool_result}")
                            break
                    
                    # Add tool result to messages
                    messages.append(ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call['id']
                    ))
                
                # Get final response with tool results
                final_response = self.llm_with_tools.invoke(messages)
                print("\n===== LLM Answer (with tool results) =====\n" + final_response.content + "\n==========================================\n")
                return final_response.content
            else:
                print("   ℹ️  No MCP tools were used for this query")
                # Print the answer in the terminal
                print("\n===== LLM Answer =====\n" + response.content + "\n======================\n")
                return response.content
                
        except Exception as e:
            return f"❌ Error processing specific question: {str(e)}"
    
    def find_exact_value(self, query: str, data: str) -> str:
        """
        Find an exact value in the provided data.
        
        Args:
            query: What to search for
            data: The data to search in
            
        Returns:
            The exact value or location
        """
        try:
            messages = [
                SystemMessage(content="You are an expert at finding exact values and information in data."),
                HumanMessage(content=f"""Find the exact answer to this query in the provided data.

Query: {query}

Data:
{data}

Provide only the specific answer requested, with references if applicable.""")
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"❌ Error finding exact value: {str(e)}"
    
    def locate_information(self, search_term: str, location_context: str) -> str:
        """
        Locate specific information in a given context.
        
        Args:
            search_term: The specific term or information to locate
            location_context: The context in which to search
            
        Returns:
            Location and details of the found information
        """
        try:
            messages = [
                SystemMessage(content="You are an expert at locating specific information precisely."),
                HumanMessage(content=f"""Locate the following specific information:

Search for: {search_term}

Context:
{location_context}

Provide the exact location (line number, section, etc.) and the specific information found.""")
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"❌ Error locating information: {str(e)}"
    
    def get_specific_detail(self, question: str, detail_type: str = "general") -> str:
        """
        Get a specific detail based on the question.
        
        Args:
            question: The specific question to answer
            detail_type: Type of detail ('value', 'name', 'date', 'code', 'general')
            
        Returns:
            The specific detail requested
        """
        try:
            detail_prompts = {
                "value": "Find and return the exact value requested:",
                "name": "Find and return the exact name or identifier requested:",
                "date": "Find and return the exact date or timestamp requested:",
                "code": "Find and return the exact code or reference number requested:",
                "general": "Find and return the exact information requested:"
            }
            
            prompt = detail_prompts.get(detail_type, detail_prompts["general"])
            
            messages = [
                SystemMessage(content="You are an expert at finding specific details with precision."),
                HumanMessage(content=f"{prompt}\n\nQuestion: {question}")
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"❌ Error getting specific detail: {str(e)}"


def main():
    """Main function to test the Specific Task Expert agent."""
    print("=" * 60)
    print("Specific Task Expert Agent - Test Mode")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
        api_key = input("\nEnter your OpenAI API key (or press Enter to skip): ").strip()
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        else:
            print("\n⚠️  Continuing without API key (will fail when making API calls)\n")
            return
    
    try:
        agent = SpecificTaskExpertAgent()
        
        # Test examples
        print("\n🔍 Testing with a specific question...\n")
        test_question = "What was the exact error code in line 45?"
        print(f"Question: {test_question}\n")
        
        response = agent.process_specific_question(test_question)
        print("Response:")
        print(response)
        
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
