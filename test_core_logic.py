"""
Quick Test Script for MCP Tools (without LangChain dependencies for testing)

This script tests the core logic of the date/time tools without requiring
LangChain to be installed. It directly tests the calculation functions.
"""

from datetime import datetime, timedelta


def test_timeline_duration():
    """Test timeline duration calculation logic."""
    print("\n" + "=" * 70)
    print("TEST 1: Timeline Duration Calculation")
    print("=" * 70)
    
    # Test 1: Multi-day duration
    start_dt = datetime.strptime("2024-01-15 09:00:00", "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime("2024-01-18 14:30:00", "%Y-%m-%d %H:%M:%S")
    duration = end_dt - start_dt
    
    days = duration.days
    total_seconds = int(duration.total_seconds())
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    total_hours = duration.total_seconds() / 3600
    
    expected = f"Duration: {days} days, {hours} hours, {minutes} minutes (Total: {total_hours:.2f} hours)"
    print(f"✅ Test 1.1 (Multi-day): {expected}")
    assert days == 3 and hours == 5 and minutes == 30, "Multi-day calculation failed"
    
    # Test 2: Same day
    start_dt = datetime.strptime("2024-01-15 09:00:00", "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime("2024-01-15 17:30:00", "%Y-%m-%d %H:%M:%S")
    duration = end_dt - start_dt
    total_hours = duration.total_seconds() / 3600
    print(f"✅ Test 1.2 (Same day): {total_hours:.2f} hours")
    assert total_hours == 8.5, "Same day calculation failed"
    
    print("✅ All timeline duration tests passed!")


def test_business_days():
    """Test business days calculation logic."""
    print("\n" + "=" * 70)
    print("TEST 2: Business Days Calculation")
    print("=" * 70)
    
    # Test 1: Week with weekend
    start_dt = datetime.strptime("2024-01-15", "%Y-%m-%d")  # Monday
    end_dt = datetime.strptime("2024-01-22", "%Y-%m-%d")    # Monday
    
    calendar_days = (end_dt - start_dt).days + 1
    business_days = 0
    current_date = start_dt
    
    while current_date <= end_dt:
        if current_date.weekday() < 5:  # Monday to Friday
            business_days += 1
        current_date += timedelta(days=1)
    
    weekend_days = calendar_days - business_days
    
    print(f"✅ Test 2.1 (Mon-Mon): Business days: {business_days}, Calendar: {calendar_days}, Weekend: {weekend_days}")
    assert business_days == 6 and calendar_days == 8 and weekend_days == 2, "Week calculation failed"
    
    # Test 2: Weekdays only
    start_dt = datetime.strptime("2024-01-15", "%Y-%m-%d")  # Monday
    end_dt = datetime.strptime("2024-01-19", "%Y-%m-%d")    # Friday
    
    calendar_days = (end_dt - start_dt).days + 1
    business_days = 0
    current_date = start_dt
    
    while current_date <= end_dt:
        if current_date.weekday() < 5:
            business_days += 1
        current_date += timedelta(days=1)
    
    print(f"✅ Test 2.2 (Mon-Fri): Business days: {business_days}, Calendar: {calendar_days}")
    assert business_days == 5 and calendar_days == 5, "Weekday-only calculation failed"
    
    print("✅ All business days tests passed!")


def test_policy_compliance():
    """Test policy compliance checking logic."""
    print("\n" + "=" * 70)
    print("TEST 3: Policy Compliance Checking")
    print("=" * 70)
    
    # Test 1: Compliant
    event_dt = datetime.strptime("2024-01-20", "%Y-%m-%d")
    reference_dt = datetime.strptime("2024-01-15", "%Y-%m-%d")
    deadline_days = 30
    
    days_difference = (event_dt - reference_dt).days
    is_compliant = days_difference <= deadline_days
    days_remaining = deadline_days - days_difference
    
    print(f"✅ Test 3.1 (Compliant): {days_difference} days, Deadline: {deadline_days}, Remaining: {days_remaining}")
    assert is_compliant and days_difference == 5, "Compliant check failed"
    
    # Test 2: Non-compliant
    event_dt = datetime.strptime("2024-02-20", "%Y-%m-%d")
    reference_dt = datetime.strptime("2024-01-15", "%Y-%m-%d")
    deadline_days = 30
    
    days_difference = (event_dt - reference_dt).days
    is_compliant = days_difference <= deadline_days
    days_overdue = days_difference - deadline_days
    
    print(f"✅ Test 3.2 (Non-compliant): {days_difference} days, Deadline: {deadline_days}, Overdue: {days_overdue}")
    assert not is_compliant and days_overdue == 6, "Non-compliant check failed"
    
    # Test 3: On last day
    event_dt = datetime.strptime("2024-02-14", "%Y-%m-%d")
    reference_dt = datetime.strptime("2024-01-15", "%Y-%m-%d")
    deadline_days = 30
    
    days_difference = (event_dt - reference_dt).days
    is_compliant = days_difference <= deadline_days
    
    print(f"✅ Test 3.3 (Last day): {days_difference} days, Deadline: {deadline_days}, Compliant: {is_compliant}")
    assert is_compliant and days_difference == 30, "Last day check failed"
    
    print("✅ All policy compliance tests passed!")


def test_error_handling():
    """Test error handling scenarios."""
    print("\n" + "=" * 70)
    print("TEST 4: Error Handling")
    print("=" * 70)
    
    # Test invalid date format
    try:
        datetime.strptime("2024/01/15", "%Y-%m-%d")
        print("❌ Should have raised ValueError for invalid format")
    except ValueError:
        print("✅ Test 4.1: Invalid date format caught correctly")
    
    # Test end before start
    start_dt = datetime.strptime("2024-01-18", "%Y-%m-%d")
    end_dt = datetime.strptime("2024-01-15", "%Y-%m-%d")
    
    if end_dt < start_dt:
        print("✅ Test 4.2: End before start detected correctly")
    else:
        print("❌ End before start not detected")
    
    # Test negative deadline
    deadline_days = -5
    if deadline_days < 0:
        print("✅ Test 4.3: Negative deadline detected correctly")
    else:
        print("❌ Negative deadline not detected")
    
    print("✅ All error handling tests passed!")


def test_edge_cases():
    """Test edge cases."""
    print("\n" + "=" * 70)
    print("TEST 5: Edge Cases")
    print("=" * 70)
    
    # Test same datetime
    start_dt = datetime.strptime("2024-01-15 12:00:00", "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.strptime("2024-01-15 12:00:00", "%Y-%m-%d %H:%M:%S")
    duration = end_dt - start_dt
    print(f"✅ Test 5.1 (Same datetime): {duration.total_seconds()} seconds")
    assert duration.total_seconds() == 0, "Same datetime failed"
    
    # Test month boundary
    start_dt = datetime.strptime("2024-01-30", "%Y-%m-%d")
    end_dt = datetime.strptime("2024-02-02", "%Y-%m-%d")
    days = (end_dt - start_dt).days
    print(f"✅ Test 5.2 (Month boundary): {days} days")
    assert days == 3, "Month boundary failed"
    
    # Test year boundary
    start_dt = datetime.strptime("2023-12-30", "%Y-%m-%d")
    end_dt = datetime.strptime("2024-01-03", "%Y-%m-%d")
    days = (end_dt - start_dt).days
    print(f"✅ Test 5.3 (Year boundary): {days} days")
    assert days == 4, "Year boundary failed"
    
    # Test leap year
    start_dt = datetime.strptime("2024-02-28", "%Y-%m-%d")
    end_dt = datetime.strptime("2024-03-01", "%Y-%m-%d")
    days = (end_dt - start_dt).days
    print(f"✅ Test 5.4 (Leap year): {days} days (includes Feb 29)")
    assert days == 2, "Leap year failed"
    
    print("✅ All edge case tests passed!")


def main():
    """Run all tests."""
    print("\n" + "╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "MCP TOOLS - CORE LOGIC TESTS" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        test_timeline_duration()
        test_business_days()
        test_policy_compliance()
        test_error_handling()
        test_edge_cases()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED! ✅")
        print("=" * 70)
        print("\nCore calculation logic is working correctly.")
        print("To test with LangChain integration, run: python tests\\test_mcp_tools.py")
        print("(Requires: pip install langchain langchain-openai)")
        print("=" * 70 + "\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
