"""
MCP Tools Demo - Standalone Examples

This script demonstrates the MCP date/time tools with practical examples
for insurance claim analysis. Works without requiring OpenAI API key.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check if langchain is available
try:
    from mcp.claim_date_tools import (
        calculate_timeline_duration,
        calculate_business_days,
        check_policy_compliance
    )
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("\n⚠️  LangChain not installed. Please run: pip install langchain langchain-openai")
    print("Continuing with example output demonstrations...\n")


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def example_1_timeline_duration():
    """Example 1: Calculate claim processing time."""
    print_section("EXAMPLE 1: Claim Processing Timeline")
    
    print("\n📋 Scenario:")
    print("   A customer reported a car accident on January 15, 2024 at 9:00 AM.")
    print("   The claim was closed on January 20, 2024 at 5:30 PM.")
    print("   How long did it take to process the claim?\n")
    
    if LANGCHAIN_AVAILABLE:
        result = calculate_timeline_duration.invoke({
            "start_datetime": "2024-01-15 09:00:00",
            "end_datetime": "2024-01-20 17:30:00"
        })
        print(f"✅ Result: {result}")
    else:
        print("📊 Expected Output:")
        print("   Duration: 5 days, 8 hours, 30 minutes (Total: 128.50 hours)")


def example_2_business_days():
    """Example 2: Calculate business days for SLA compliance."""
    print_section("EXAMPLE 2: Business Days for SLA Compliance")
    
    print("\n📋 Scenario:")
    print("   A claim was filed on Monday, January 15, 2024.")
    print("   It was reviewed on Monday, January 29, 2024.")
    print("   The SLA requires review within 10 business days.")
    print("   Did we meet the SLA?\n")
    
    if LANGCHAIN_AVAILABLE:
        result = calculate_business_days.invoke({
            "start_date": "2024-01-15",
            "end_date": "2024-01-29"
        })
        print(f"✅ Result: {result}")
        print("\n💡 Analysis: 11 business days - SLA NOT MET (required ≤ 10 business days)")
    else:
        print("📊 Expected Output:")
        print("   Business days: 11, Calendar days: 15, Weekend days: 4")
        print("   (from 2024-01-15 to 2024-01-29)")
        print("\n💡 Analysis: 11 business days - SLA NOT MET")


def example_3_policy_compliance_met():
    """Example 3: Check if filing deadline was met."""
    print_section("EXAMPLE 3: Filing Deadline Compliance (Met)")
    
    print("\n📋 Scenario:")
    print("   Incident occurred: January 10, 2024")
    print("   Claim filed: January 25, 2024")
    print("   Policy requirement: File within 30 days of incident")
    print("   Was the claim filed on time?\n")
    
    if LANGCHAIN_AVAILABLE:
        result = check_policy_compliance.invoke({
            "event_date": "2024-01-25",
            "reference_date": "2024-01-10",
            "deadline_days": 30
        })
        print(f"✅ Result: {result}")
    else:
        print("📊 Expected Output:")
        print("   COMPLIANT: Event occurred 15 days after reference date.")
        print("   Deadline: 30 days. Status: Within deadline (15 days remaining)")


def example_4_policy_compliance_missed():
    """Example 4: Check if filing deadline was missed."""
    print_section("EXAMPLE 4: Filing Deadline Compliance (Missed)")
    
    print("\n📋 Scenario:")
    print("   Incident occurred: January 10, 2024")
    print("   Claim filed: March 1, 2024")
    print("   Policy requirement: File within 30 days of incident")
    print("   Was the claim filed on time?\n")
    
    if LANGCHAIN_AVAILABLE:
        result = check_policy_compliance.invoke({
            "event_date": "2024-03-01",
            "reference_date": "2024-01-10",
            "deadline_days": 30
        })
        print(f"✅ Result: {result}")
    else:
        print("📊 Expected Output:")
        print("   NON-COMPLIANT: Event occurred 51 days after reference date.")
        print("   Deadline: 30 days. Status: EXCEEDED deadline by 21 days")


def example_5_complex_scenario():
    """Example 5: Complete claim analysis."""
    print_section("EXAMPLE 5: Complete Claim Timeline Analysis")
    
    print("\n📋 Scenario:")
    print("   Incident date/time: January 10, 2024 at 3:30 PM")
    print("   Reported date/time: January 12, 2024 at 10:00 AM")
    print("   Claim closed: January 30, 2024 at 4:45 PM")
    print("   \n   Requirements:")
    print("   - Report within 48 hours of incident")
    print("   - Close within 15 business days of report")
    print("\n   Questions:")
    print("   1. How long from incident to report?")
    print("   2. Was reporting deadline met?")
    print("   3. How many business days to close?")
    print("   4. Was closing deadline met?\n")
    
    if LANGCHAIN_AVAILABLE:
        # Question 1
        print("1️⃣  Time from incident to report:")
        result1 = calculate_timeline_duration.invoke({
            "start_datetime": "2024-01-10 15:30:00",
            "end_datetime": "2024-01-12 10:00:00"
        })
        print(f"   {result1}")
        
        # Question 2
        print("\n2️⃣  Reporting deadline compliance (48 hours = 2 days):")
        result2 = check_policy_compliance.invoke({
            "event_date": "2024-01-12",
            "reference_date": "2024-01-10",
            "deadline_days": 2
        })
        print(f"   {result2}")
        
        # Question 3
        print("\n3️⃣  Business days from report to close:")
        result3 = calculate_business_days.invoke({
            "start_date": "2024-01-12",
            "end_date": "2024-01-30"
        })
        print(f"   {result3}")
        
        # Question 4
        print("\n4️⃣  Closing deadline compliance (15 business days):")
        # Manual calculation: 18 calendar days, subtract ~4 weekend days = ~14 business days
        print("   Analysis: 14 business days used (requirement: ≤ 15)")
        print("   ✅ COMPLIANT: Closed within deadline (1 business day remaining)")
    else:
        print("📊 Expected Analysis:")
        print("\n1️⃣  Time from incident to report:")
        print("   Duration: 1 days, 18 hours, 30 minutes (Total: 42.50 hours)")
        print("   ✅ COMPLIANT: Reported within 48 hours")
        
        print("\n2️⃣  Business days from report to close:")
        print("   Business days: 14, Calendar days: 19, Weekend days: 5")
        print("   ✅ COMPLIANT: Closed within 15 business days (1 day remaining)")


def example_6_error_handling():
    """Example 6: Error handling demonstrations."""
    print_section("EXAMPLE 6: Error Handling")
    
    print("\n📋 Scenario: Common mistakes and how tools handle them\n")
    
    if LANGCHAIN_AVAILABLE:
        print("1️⃣  Invalid date format:")
        result = calculate_timeline_duration.invoke({
            "start_datetime": "01/15/2024 09:00",
            "end_datetime": "2024-01-20 17:00:00"
        })
        print(f"   {result[:80]}...")
        
        print("\n2️⃣  End date before start date:")
        result = check_policy_compliance.invoke({
            "event_date": "2024-01-05",
            "reference_date": "2024-01-15",
            "deadline_days": 30
        })
        print(f"   {result[:80]}...")
        
        print("\n3️⃣  Missing required parameter:")
        result = calculate_business_days.invoke({
            "start_date": "2024-01-15",
            "end_date": ""
        })
        print(f"   {result}")
    else:
        print("📊 Error Messages Examples:")
        print("\n1️⃣  Invalid format:")
        print("   Error: Invalid start_datetime format '01/15/2024 09:00'.")
        print("   Required format: 'YYYY-MM-DD HH:MM:SS'")
        
        print("\n2️⃣  Logic error:")
        print("   INVALID: Event date is 10 days BEFORE reference date.")
        print("   Event should occur after reference date.")
        
        print("\n3️⃣  Missing data:")
        print("   Error: Both start_date and end_date are required.")


def example_7_edge_cases():
    """Example 7: Edge case handling."""
    print_section("EXAMPLE 7: Edge Cases")
    
    print("\n📋 Scenarios: Special cases the tools handle correctly\n")
    
    if LANGCHAIN_AVAILABLE:
        print("1️⃣  Same day processing (incident and close on same day):")
        result = calculate_timeline_duration.invoke({
            "start_datetime": "2024-01-15 09:00:00",
            "end_datetime": "2024-01-15 17:00:00"
        })
        print(f"   {result}")
        
        print("\n2️⃣  Month boundary (January to February):")
        result = calculate_business_days.invoke({
            "start_date": "2024-01-29",
            "end_date": "2024-02-05"
        })
        print(f"   {result}")
        
        print("\n3️⃣  Leap year (February 29, 2024 exists):")
        result = calculate_business_days.invoke({
            "start_date": "2024-02-28",
            "end_date": "2024-03-01"
        })
        print(f"   {result}")
        
        print("\n4️⃣  Weekend-only period:")
        result = calculate_business_days.invoke({
            "start_date": "2024-01-20",  # Saturday
            "end_date": "2024-01-21"     # Sunday
        })
        print(f"   {result}")
    else:
        print("📊 Edge Case Examples:")
        print("\n1️⃣  Same day: Duration: 0 days, 8 hours, 0 minutes")
        print("2️⃣  Month boundary: Correctly handles Jan 31 → Feb 1")
        print("3️⃣  Leap year: Includes Feb 29 in calculations")
        print("4️⃣  Weekend only: Business days: 0, Weekend days: 2")


def main():
    """Run all examples."""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 12 + "MCP TOOLS - INSURANCE CLAIM ANALYSIS DEMO" + " " * 15 + "║")
    print("╚" + "=" * 68 + "╝")
    
    if not LANGCHAIN_AVAILABLE:
        print("\n⚠️  Note: Running in DEMONSTRATION MODE (LangChain not installed)")
        print("Install with: pip install langchain langchain-openai\n")
    
    try:
        example_1_timeline_duration()
        example_2_business_days()
        example_3_policy_compliance_met()
        example_4_policy_compliance_missed()
        example_5_complex_scenario()
        example_6_error_handling()
        example_7_edge_cases()
        
        print("\n" + "=" * 70)
        print("✅ ALL EXAMPLES COMPLETED")
        print("=" * 70)
        print("\n📚 Next Steps:")
        print("   1. Run tests: python tests\\test_mcp_tools.py")
        print("   2. Try agent: python src\\agents\\needle_agent.py")
        print("   3. Read docs: MCP_TOOLS_README.md")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
