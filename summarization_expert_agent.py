"""
Summarization Expert Agent using LangChain
Handles broad questions, summaries, and timeline-oriented queries.
Enhanced with Supabase vector search for context retrieval.
"""

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from typing import Optional
from dotenv import load_dotenv
from supabase.client import create_client
import os
from mcp.claim_date_tools import (
    calculate_timeline_duration,
    calculate_business_days,
    check_policy_compliance
)

# Load environment variables
load_dotenv()


class SummarizationExpertAgent:
    """
    A specialized agent for handling broad questions, summaries, and timeline-oriented queries.
    This agent excels at providing comprehensive overviews and high-level insights.
    Enhanced with Supabase vector search for retrieving relevant context.
    """
    
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.7):
        """
        Initialize the Summarization Expert agent.
        
        Args:
            model_name: The LLM model to use
            temperature: Temperature for creative but coherent summaries
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.supabase_client = None
        
        # Initialize MCP date/time tools
        self.date_tools = [
            calculate_timeline_duration,
            calculate_business_days,
            check_policy_compliance
        ]
        # Bind tools to LLM for automatic tool calling
        self.llm_with_tools = self.llm.bind_tools(self.date_tools)
        
        # Initialize Supabase if credentials are available
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
            if supabase_url and supabase_key:
                self.supabase_client = create_client(supabase_url, supabase_key)
                print("✅ Supabase connected for context retrieval")
        except Exception as e:
            print(f"⚠️ Supabase connection failed: {str(e)}")
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 3, table_name: str = "summary_chunks") -> list:
        """
        Retrieve relevant chunks from Supabase vector database.
        
        Args:
            query: The user's query
            top_k: Number of top relevant chunks to retrieve
            table_name: Name of the Supabase table
            
        Returns:
            List of relevant chunk texts
        """
        if not self.supabase_client:
            print("⚠️ Supabase not available, proceeding without context")
            return []
        
        try:
            # Create query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            # Search for similar chunks
            results = self.supabase_client.rpc(
                f"{table_name}_search",
                {
                    "query_embedding": query_embedding,
                    "match_count": top_k
                }
            ).execute()
            
            if results.data:
                print(f"✅ Retrieved {len(results.data)} relevant chunks from Supabase")
                return [chunk["content"] for chunk in results.data]
            else:
                print("⚠️ No relevant chunks found")
                return []
                
        except Exception as e:
            print(f"⚠️ Error retrieving chunks: {str(e)}")
            return []
        
    def process_broad_question(self, user_input: str, context: Optional[str] = None) -> str:
        """
        Process a broad question and generate a comprehensive summary or overview.
        Now enhanced with Supabase vector search for retrieving relevant context.
        
        Args:
            user_input: The user's broad question
            context: Optional context or data to summarize
            
        Returns:
            A comprehensive summary or overview response
        """
        try:
            print(f"\n🔍 Processing broad question: {user_input}")
            
            # Retrieve relevant chunks from Supabase
            relevant_chunks = self.retrieve_relevant_chunks(user_input, top_k=3)
            
            system_prompt = """You are a Summarization Expert AI assistant specializing in:
- Creating comprehensive summaries and overviews
- Analyzing timelines and trends
- Providing high-level insights and strategic perspectives
- Breaking down complex topics into understandable overviews
- Identifying key themes, patterns, and important highlights

Your responses should be:
1. Well-structured with clear sections
2. Comprehensive yet concise
3. Focused on the big picture and key insights
4. Easy to understand and actionable
5. Include relevant timelines when applicable

You have access to the following MCP tools for date/time calculations:
- calculate_timeline_duration: Calculate time between two dates
- calculate_business_days: Calculate business days between dates
- check_policy_compliance: Check if dates meet policy deadlines

Use these tools when the question involves date/time calculations, timelines, or compliance checks.

Always provide thorough, professional summaries that give users a complete understanding of the topic."""

            # Build the user message with retrieved context
            user_message = f"User Question: {user_input}"
            
            # Add retrieved chunks as context
            if relevant_chunks:
                user_message += "\n\n--- Retrieved Relevant Context from Knowledge Base ---"
                for i, chunk in enumerate(relevant_chunks, 1):
                    user_message += f"\n\n[Context {i}]:\n{chunk}"
                user_message += "\n\n--- End of Retrieved Context ---"
            
            if context:
                user_message += f"\n\nAdditional Context/Data to analyze:\n{context}"
            
            user_message += "\n\nPlease provide a comprehensive summary or overview addressing this broad question, using the retrieved context where relevant."
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]
            
            print("🤖 Sending request to LLM...")
            print("🔧 Available MCP Tools: calculate_timeline_duration, calculate_business_days, check_policy_compliance")
            
            # Invoke the LLM with tools
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
                print("✅ Received response from LLM (with tool results)\n")
                return final_response.content
            else:
                print("   ℹ️  No MCP tools were used for this query")
                print("✅ Received response from LLM\n")
                return response.content
            
        except Exception as e:
            return f"❌ Error processing broad question: {str(e)}"
    
    def generate_summary(self, content: str, summary_type: str = "general") -> str:
        """
        Generate different types of summaries.
        
        Args:
            content: The content to summarize
            summary_type: Type of summary ('general', 'timeline', 'executive', 'technical')
            
        Returns:
            The generated summary
        """
        try:
            summary_prompts = {
                "general": "Provide a comprehensive general summary of the following content:",
                "timeline": "Create a timeline-based summary highlighting key events and their sequence:",
                "executive": "Provide an executive summary focusing on key decisions, outcomes, and strategic insights:",
                "technical": "Create a technical summary highlighting key technical details, architecture, and implementation:"
            }
            
            prompt = summary_prompts.get(summary_type, summary_prompts["general"])
            
            messages = [
                SystemMessage(content="You are an expert at creating clear, comprehensive summaries."),
                HumanMessage(content=f"{prompt}\n\n{content}")
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"❌ Error generating summary: {str(e)}"
    
    def analyze_timeline(self, events: str) -> str:
        """
        Analyze and summarize timeline-oriented information.
        
        Args:
            events: Timeline events or chronological data
            
        Returns:
            Timeline analysis and summary
        """
        try:
            messages = [
                SystemMessage(content="You are an expert at analyzing timelines and chronological data."),
                HumanMessage(content=f"""Analyze the following timeline information and provide:
1. A chronological overview
2. Key milestones and important events
3. Trends or patterns over time
4. Overall timeline summary

Timeline Data:
{events}""")
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"❌ Error analyzing timeline: {str(e)}"
    
    def get_overview(self, topic: str, aspects: Optional[list] = None) -> str:
        """
        Generate a comprehensive overview of a topic.
        
        Args:
            topic: The topic to provide an overview of
            aspects: Specific aspects to focus on (optional)
            
        Returns:
            Comprehensive overview
        """
        try:
            aspect_text = ""
            if aspects:
                aspect_text = f"\n\nFocus on these specific aspects:\n" + "\n".join(f"- {a}" for a in aspects)
            
            messages = [
                SystemMessage(content="You are an expert at providing comprehensive overviews."),
                HumanMessage(content=f"Provide a comprehensive overview of: {topic}{aspect_text}")
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            return f"❌ Error generating overview: {str(e)}"


def main():
    """Main function to test the Summarization Expert agent."""
    print("=" * 60)
    print("Summarization Expert Agent - Test Mode")
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
        agent = SummarizationExpertAgent()
        
        # Test examples
        print("\n📊 Testing with a broad question...\n")
        test_question = "Summarize the key developments in AI over the past year"
        print(f"Question: {test_question}\n")
        
        response = agent.process_broad_question(test_question)
        print("Response:")
        print(response)
        
        print("\n" + "=" * 60)
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
