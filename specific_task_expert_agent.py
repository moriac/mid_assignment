"""
Specific Task Expert Agent using LangChain
Handles Type 1 questions: "Needle in Haystack" - specific, precise questions.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from typing import Optional
import os
from hierarchical_retriever import get_claim_retriever
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
    
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0, use_hierarchical_retrieval=True):
        """
        Initialize the Specific Task Expert agent.
        
        Args:
            model_name: The LLM model to use
            temperature: Temperature set to 0 for precise, consistent answers
            use_hierarchical_retrieval: If True, use hierarchical auto-merging retrieval (default: True)
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
        
        # Initialize hierarchical retriever
        self.use_hierarchical_retrieval = use_hierarchical_retrieval
        self.hierarchical_retriever = None
        if use_hierarchical_retrieval:
            print("Initializing hierarchical auto-merging retrieval system...")
            try:
                self.hierarchical_retriever = get_claim_retriever(use_supabase=False)
                print("✓ Hierarchical retriever ready")
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize hierarchical retriever: {e}")
                print("   Falling back to no retrieval")
                self.use_hierarchical_retrieval = False
    
    def _get_metadata_from_retriever(self) -> Optional[dict]:
        """
        Get metadata from the first node in the retriever's index.
        
        Returns:
            Dictionary of metadata or None
        """
        if not self.use_hierarchical_retrieval or not self.hierarchical_retriever:
            return None
        
        try:
            # Retrieve any node to get metadata (metadata is attached to all nodes from the document)
            test_nodes = self.hierarchical_retriever.retrieve("claim information")
            if test_nodes and hasattr(test_nodes[0], 'node') and hasattr(test_nodes[0].node, 'metadata'):
                return test_nodes[0].node.metadata
        except:
            pass
        
        return None
    
    def _answer_from_metadata(self, user_input: str, metadata: dict) -> Optional[str]:
        """
        Try to answer the question directly from metadata if possible.
        Does NOT answer calculation/analysis questions - those need full context + tools.
        
        Args:
            user_input: The user's question
            metadata: Extracted metadata dictionary
            
        Returns:
            Answer string if found in metadata, None otherwise
        """
        query_lower = user_input.lower()
        
        # Skip metadata-only answers for questions that need calculation or analysis
        calculation_keywords = ['how many', 'calculate', 'elapsed', 'duration', 'between', 'difference', 'days between']
        if any(keyword in query_lower for keyword in calculation_keywords):
            return None  # Let the full system handle this with MCP tools
        
        # Incident date queries
        if any(phrase in query_lower for phrase in ['incident date', 'when did the incident occur', 'date of incident', 'loss date']):
            if metadata.get('incident_date_display'):
                return f"The incident occurred on {metadata['incident_date_display']}."
            elif metadata.get('incident_date'):
                return f"The incident occurred on {metadata['incident_date']}."
        
        # Claim filed date queries
        if any(phrase in query_lower for phrase in ['claim filed', 'when was the claim filed', 'filing date', 'claim date']):
            if metadata.get('claim_filed_date_display'):
                return f"The claim was filed on {metadata['claim_filed_date_display']}."
            elif metadata.get('claim_filed_date'):
                return f"The claim was filed on {metadata['claim_filed_date']}."
        
        # Claim number queries
        if any(phrase in query_lower for phrase in ['claim number', 'claim id', 'claim #']):
            if metadata.get('claim_number'):
                return f"The claim number is {metadata['claim_number']}."
        
        # Policy number queries
        if any(phrase in query_lower for phrase in ['policy number', 'policy id', 'policy #']):
            if metadata.get('policy_number'):
                return f"The policy number is {metadata['policy_number']}."
        
        # Claimant/Policyholder queries
        if any(phrase in query_lower for phrase in ['claimant', 'who is the claimant', 'policyholder', 'who is the policyholder']):
            if 'policyholder' in query_lower and metadata.get('policyholder'):
                return f"The policyholder is {metadata['policyholder']}."
            elif metadata.get('claimant'):
                return f"The claimant is {metadata['claimant']}."
        
        # Claim amount queries
        if any(phrase in query_lower for phrase in ['claim amount', 'total claim', 'how much']):
            if metadata.get('claim_amount'):
                try:
                    amount = float(metadata['claim_amount'])
                    return f"The claim amount is ${amount:,.2f}."
                except:
                    return f"The claim amount is ${metadata['claim_amount']}."
        
        # Location queries
        if any(phrase in query_lower for phrase in ['location', 'where', 'address']):
            if metadata.get('loss_location'):
                return f"The loss location is {metadata['loss_location']}."
        
        return None
        
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
            # Step 1: Try to answer from metadata first (most accurate)
            metadata = self._get_metadata_from_retriever()
            if metadata:
                metadata_answer = self._answer_from_metadata(user_input, metadata)
                if metadata_answer:
                    print(f"\n✅ Answered directly from document metadata (100% accurate)")
                    print(f"   Metadata used: {[k for k, v in metadata.items() if v]}")
                    return metadata_answer
            
            # Step 2: Use hierarchical retrieval for complex queries
            context_str = None
            if self.use_hierarchical_retrieval and self.hierarchical_retriever:
                print(f"\n🔍 Retrieving context using hierarchical auto-merging retrieval...")
                retrieved_nodes = self.hierarchical_retriever.retrieve(user_input)
                
                if retrieved_nodes:
                    print(f"   Retrieved {len(retrieved_nodes)} node(s) after auto-merging")
                    
                    # Add metadata to context for complex queries (like date calculations)
                    if metadata:
                        metadata_context = "\n📋 VERIFIED METADATA:\n"
                        if metadata.get('incident_date'):
                            metadata_context += f"- Incident Date: {metadata['incident_date']}\n"
                        if metadata.get('claim_filed_date'):
                            metadata_context += f"- Claim Filed Date: {metadata['claim_filed_date']}\n"
                        if metadata.get('claim_number'):
                            metadata_context += f"- Claim Number: {metadata['claim_number']}\n"
                        if metadata.get('policy_number'):
                            metadata_context += f"- Policy Number: {metadata['policy_number']}\n"
                        if metadata.get('claim_amount'):
                            metadata_context += f"- Claim Amount: ${metadata['claim_amount']}\n"
                        metadata_context += "\n"
                    
                        # Extract text from retrieved nodes
                        relevant_chunks = [node.text for node in retrieved_nodes]
                        context_str = metadata_context + "\n---\n".join(relevant_chunks)
                    else:
                        relevant_chunks = [node.text for node in retrieved_nodes]
                        context_str = "\n---\n".join(relevant_chunks)
                else:
                    print("   No relevant nodes found")
            else:
                print("\n⚠️ Hierarchical retrieval not available, using provided context only")

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
