"""
Quick Verification Script - Check if MCP Tools are Bound to Agents
This script simply verifies the tool binding without making API calls.
"""

from specific_task_expert_agent import SpecificTaskExpertAgent
from summarization_expert_agent import SummarizationExpertAgent

def verify_tool_binding():
    """Verify that both agents have MCP tools properly bound."""
    print("=" * 70)
    print("🔍 VERIFYING MCP TOOL BINDING")
    print("=" * 70)
    
    # Test Specific Task Expert Agent
    print("\n1️⃣ Specific Task Expert Agent:")
    print("-" * 70)
    try:
        specific_agent = SpecificTaskExpertAgent()
        
        # Check if tools are defined
        if hasattr(specific_agent, 'date_tools'):
            print(f"   ✅ MCP tools loaded: {len(specific_agent.date_tools)} tools")
            for tool in specific_agent.date_tools:
                print(f"      - {tool.name}")
        else:
            print("   ❌ No date_tools attribute found")
        
        # Check if tools are bound to LLM
        if hasattr(specific_agent, 'llm_with_tools'):
            print("   ✅ Tools are bound to LLM (llm_with_tools exists)")
        else:
            print("   ❌ Tools NOT bound to LLM (no llm_with_tools)")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test Summarization Expert Agent
    print("\n2️⃣ Summarization Expert Agent:")
    print("-" * 70)
    try:
        summary_agent = SummarizationExpertAgent()
        
        # Check if tools are defined
        if hasattr(summary_agent, 'date_tools'):
            print(f"   ✅ MCP tools loaded: {len(summary_agent.date_tools)} tools")
            for tool in summary_agent.date_tools:
                print(f"      - {tool.name}")
        else:
            print("   ❌ No date_tools attribute found")
        
        # Check if tools are bound to LLM
        if hasattr(summary_agent, 'llm_with_tools'):
            print("   ✅ Tools are bound to LLM (llm_with_tools exists)")
        else:
            print("   ❌ Tools NOT bound to LLM (no llm_with_tools)")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    print("""
Both agents should show:
  ✅ MCP tools loaded: 3 tools
     - calculate_timeline_duration
     - calculate_business_days  
     - check_policy_compliance
  ✅ Tools are bound to LLM (llm_with_tools exists)

This confirms that:
  1. MCP tools are imported correctly
  2. Tools are bound to the LLM via bind_tools()
  3. Agents will automatically use tools when processing questions

To test tool usage with actual questions, run:
  python test_mcp_tool_binding.py
""")
    print("=" * 70)

if __name__ == "__main__":
    verify_tool_binding()
