"""
Summarization Expert Agent using LangChain
Handles broad questions, summaries, and timeline-oriented queries.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Optional
import os


class SummarizationExpertAgent:
    """
    A specialized agent for handling broad questions, summaries, and timeline-oriented queries.
    This agent excels at providing comprehensive overviews and high-level insights.
    """
    
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.7):
        """
        Initialize the Summarization Expert agent.
        
        Args:
            model_name: The LLM model to use
            temperature: Temperature for creative but coherent summaries
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        
    def process_broad_question(self, user_input: str, context: Optional[str] = None) -> str:
        """
        Process a broad question and generate a comprehensive summary or overview.
        
        Args:
            user_input: The user's broad question
            context: Optional context or data to summarize
            
        Returns:
            A comprehensive summary or overview response
        """
        try:
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

Always provide thorough, professional summaries that give users a complete understanding of the topic."""

            # Build the user message
            user_message = f"User Question: {user_input}"
            
            if context:
                user_message += f"\n\nContext/Data to analyze:\n{context}"
            
            user_message += "\n\nPlease provide a comprehensive summary or overview addressing this broad question."
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]
            
            # Invoke the LLM
            response = self.llm.invoke(messages)
            
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
