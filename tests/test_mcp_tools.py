"""
Comprehensive Unit Tests for MCP Date/Time Calculation Tools.

This module contains thorough unit tests for the insurance claim analysis
date/time tools, including edge cases and error handling.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.claim_date_tools import (
    calculate_timeline_duration,
    calculate_business_days,
    check_policy_compliance
)


class TestCalculateTimelineDuration(unittest.TestCase):
    """Test cases for calculate_timeline_duration tool."""
    
    def test_same_day_different_times(self):
        """Test duration calculation within the same day."""
        result = calculate_timeline_duration.invoke({
            "start_datetime": "2024-01-15 09:00:00",
            "end_datetime": "2024-01-15 17:30:00"
        })
        self.assertIn("0 days, 8 hours, 30 minutes", result)
        self.assertIn("8.50 hours", result)
    
    def test_multi_day_duration(self):
        """Test duration calculation spanning multiple days."""
        result = calculate_timeline_duration.invoke({
            "start_datetime": "2024-01-15 09:00:00",
            "end_datetime": "2024-01-18 14:30:00"
        })
        self.assertIn("3 days, 5 hours, 30 minutes", result)
        self.assertIn("77.50 hours", result)
    
    def test_multi_week_duration(self):
        """Test duration calculation spanning multiple weeks."""
        result = calculate_timeline_duration.invoke({
            "start_datetime": "2024-01-01 10:00:00",
            "end_datetime": "2024-01-22 16:45:00"
        })
        self.assertIn("21 days", result)
        self.assertIn("6 hours, 45 minutes", result)
    
    def test_same_datetime(self):
        """Test when start and end times are identical."""
        result = calculate_timeline_duration.invoke({
            "start_datetime": "2024-01-15 12:00:00",
            "end_datetime": "2024-01-15 12:00:00"
        })
        self.assertIn("0 days, 0 hours, 0 minutes", result)
        self.assertIn("0.00 hours", result)
    
    def test_one_minute_duration(self):
        """Test minimal duration of one minute."""
        result = calculate_timeline_duration.invoke({
            "start_datetime": "2024-01-15 12:00:00",
            "end_datetime": "2024-01-15 12:01:00"
        })
        self.assertIn("0 days, 0 hours, 1 minutes", result)
    
    def test_month_boundary(self):
        """Test duration crossing month boundary."""
        result = calculate_timeline_duration.invoke({
            "start_datetime": "2024-01-30 15:00:00",
            "end_datetime": "2024-02-02 09:00:00"
        })
        self.assertIn("2 days, 18 hours", result)
    
    def test_year_boundary(self):
        """Test duration crossing year boundary."""
        result = calculate_timeline_duration.invoke({
            "start_datetime": "2023-12-30 10:00:00",
            "end_datetime": "2024-01-03 14:00:00"
        })
        self.assertIn("4 days, 4 hours", result)
    
    def test_invalid_start_format(self):
        """Test error handling for invalid start datetime format."""
        result = calculate_timeline_duration.invoke({
            "start_datetime": "2024/01/15 09:00:00",
            "end_datetime": "2024-01-15 17:00:00"
        })
        self.assertIn("Error", result)
        self.assertIn("Invalid start_datetime format", result)
        self.assertIn("YYYY-MM-DD HH:MM:SS", result)
    
    def test_invalid_end_format(self):
        """Test error handling for invalid end datetime format."""
        result = calculate_timeline_duration.invoke({
            "start_datetime": "2024-01-15 09:00:00",
            "end_datetime": "15-01-2024 17:00:00"
        })
        self.assertIn("Error", result)
        self.assertIn("Invalid end_datetime format", result)
    
    def test_end_before_start(self):
        """Test error handling when end is before start."""
        result = calculate_timeline_duration.invoke({
            "start_datetime": "2024-01-18 14:00:00",
            "end_datetime": "2024-01-15 09:00:00"
        })
        self.assertIn("Error", result)
        self.assertIn("before start datetime", result)
    
    def test_missing_start_datetime(self):
        """Test error handling for missing start datetime."""
        result = calculate_timeline_duration.invoke({
            "start_datetime": "",
            "end_datetime": "2024-01-15 17:00:00"
        })
        self.assertIn("Error", result)
        self.assertIn("required", result)
    
    def test_missing_end_datetime(self):
        """Test error handling for missing end datetime."""
        result = calculate_timeline_duration.invoke({
            "start_datetime": "2024-01-15 09:00:00",
            "end_datetime": ""
        })
        self.assertIn("Error", result)
        self.assertIn("required", result)


class TestCalculateBusinessDays(unittest.TestCase):
    """Test cases for calculate_business_days tool."""
    
    def test_weekdays_only(self):
        """Test business days calculation with only weekdays."""
        # Monday to Friday
        result = calculate_business_days.invoke({
            "start_date": "2024-01-15",  # Monday
            "end_date": "2024-01-19"     # Friday
        })
        self.assertIn("Business days: 5", result)
        self.assertIn("Calendar days: 5", result)
        self.assertIn("Weekend days: 0", result)
    
    def test_including_one_weekend(self):
        """Test business days calculation including one weekend."""
        # Monday to Monday (includes one weekend)
        result = calculate_business_days.invoke({
            "start_date": "2024-01-15",  # Monday
            "end_date": "2024-01-22"     # Monday
        })
        self.assertIn("Business days: 6", result)
        self.assertIn("Calendar days: 8", result)
        self.assertIn("Weekend days: 2", result)
    
    def test_including_two_weekends(self):
        """Test business days calculation including two weekends."""
        # Two full weeks + weekend
        result = calculate_business_days.invoke({
            "start_date": "2024-01-15",  # Monday
            "end_date": "2024-01-29"     # Monday
        })
        self.assertIn("Business days: 11", result)
        self.assertIn("Calendar days: 15", result)
        self.assertIn("Weekend days: 4", result)
    
    def test_same_date(self):
        """Test when start and end dates are the same."""
        result = calculate_business_days.invoke({
            "start_date": "2024-01-15",
            "end_date": "2024-01-15"
        })
        self.assertIn("Business days: 1", result)
        self.assertIn("Calendar days: 1", result)
    
    def test_weekend_dates(self):
        """Test calculation when dates fall on weekend."""
        # Saturday to Sunday
        result = calculate_business_days.invoke({
            "start_date": "2024-01-20",  # Saturday
            "end_date": "2024-01-21"     # Sunday
        })
        self.assertIn("Business days: 0", result)
        self.assertIn("Calendar days: 2", result)
        self.assertIn("Weekend days: 2", result)
    
    def test_friday_to_monday(self):
        """Test calculation from Friday to Monday."""
        result = calculate_business_days.invoke({
            "start_date": "2024-01-19",  # Friday
            "end_date": "2024-01-22"     # Monday
        })
        self.assertIn("Business days: 2", result)
        self.assertIn("Calendar days: 4", result)
        self.assertIn("Weekend days: 2", result)
    
    def test_month_boundary(self):
        """Test business days crossing month boundary."""
        result = calculate_business_days.invoke({
            "start_date": "2024-01-29",  # Monday
            "end_date": "2024-02-02"     # Friday
        })
        self.assertIn("Business days: 5", result)
    
    def test_year_boundary(self):
        """Test business days crossing year boundary."""
        result = calculate_business_days.invoke({
            "start_date": "2023-12-28",  # Thursday
            "end_date": "2024-01-03"     # Wednesday
        })
        # Thu, Fri, Mon, Tue, Wed = 5 business days
        self.assertIn("Business days: 5", result)
    
    def test_leap_year_february(self):
        """Test business days in February of leap year."""
        # 2024 is a leap year
        result = calculate_business_days.invoke({
            "start_date": "2024-02-26",  # Monday
            "end_date": "2024-02-29"     # Thursday (leap day)
        })
        self.assertIn("Business days: 4", result)
    
    def test_invalid_start_format(self):
        """Test error handling for invalid start date format."""
        result = calculate_business_days.invoke({
            "start_date": "01/15/2024",
            "end_date": "2024-01-25"
        })
        self.assertIn("Error", result)
        self.assertIn("Invalid start_date format", result)
        self.assertIn("YYYY-MM-DD", result)
    
    def test_invalid_end_format(self):
        """Test error handling for invalid end date format."""
        result = calculate_business_days.invoke({
            "start_date": "2024-01-15",
            "end_date": "25-01-2024"
        })
        self.assertIn("Error", result)
        self.assertIn("Invalid end_date format", result)
    
    def test_end_before_start(self):
        """Test error handling when end date is before start date."""
        result = calculate_business_days.invoke({
            "start_date": "2024-01-25",
            "end_date": "2024-01-15"
        })
        self.assertIn("Error", result)
        self.assertIn("before start date", result)
    
    def test_missing_start_date(self):
        """Test error handling for missing start date."""
        result = calculate_business_days.invoke({
            "start_date": "",
            "end_date": "2024-01-25"
        })
        self.assertIn("Error", result)
        self.assertIn("required", result)
    
    def test_missing_end_date(self):
        """Test error handling for missing end date."""
        result = calculate_business_days.invoke({
            "start_date": "2024-01-15",
            "end_date": ""
        })
        self.assertIn("Error", result)
        self.assertIn("required", result)


class TestCheckPolicyCompliance(unittest.TestCase):
    """Test cases for check_policy_compliance tool."""
    
    def test_compliant_within_deadline(self):
        """Test compliant case - event within deadline."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-01-20",
            "reference_date": "2024-01-15",
            "deadline_days": 30
        })
        self.assertIn("COMPLIANT", result)
        self.assertIn("5 days after reference date", result)
        self.assertIn("25 days remaining", result)
    
    def test_compliant_on_last_day(self):
        """Test compliant case - event on last day of deadline."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-02-14",
            "reference_date": "2024-01-15",
            "deadline_days": 30
        })
        self.assertIn("COMPLIANT", result)
        self.assertIn("30 days after reference date", result)
        self.assertIn("0 days remaining", result)
    
    def test_compliant_same_day(self):
        """Test compliant case - event on same day as reference."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-01-15",
            "reference_date": "2024-01-15",
            "deadline_days": 30
        })
        self.assertIn("COMPLIANT", result)
        self.assertIn("0 days after reference date", result)
        self.assertIn("30 days remaining", result)
    
    def test_non_compliant_exceeded_deadline(self):
        """Test non-compliant case - event exceeds deadline."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-02-20",
            "reference_date": "2024-01-15",
            "deadline_days": 30
        })
        self.assertIn("NON-COMPLIANT", result)
        self.assertIn("36 days after reference date", result)
        self.assertIn("EXCEEDED deadline by 6 days", result)
    
    def test_non_compliant_significantly_overdue(self):
        """Test non-compliant case - significantly overdue."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-03-15",
            "reference_date": "2024-01-15",
            "deadline_days": 30
        })
        self.assertIn("NON-COMPLIANT", result)
        self.assertIn("EXCEEDED deadline", result)
    
    def test_invalid_event_before_reference(self):
        """Test invalid case - event before reference date."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-01-10",
            "reference_date": "2024-01-15",
            "deadline_days": 30
        })
        self.assertIn("INVALID", result)
        self.assertIn("BEFORE reference date", result)
    
    def test_short_deadline_compliant(self):
        """Test compliance with short deadline."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-01-17",
            "reference_date": "2024-01-15",
            "deadline_days": 3
        })
        self.assertIn("COMPLIANT", result)
        self.assertIn("2 days after reference date", result)
    
    def test_short_deadline_non_compliant(self):
        """Test non-compliance with short deadline."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-01-20",
            "reference_date": "2024-01-15",
            "deadline_days": 3
        })
        self.assertIn("NON-COMPLIANT", result)
        self.assertIn("EXCEEDED deadline", result)
    
    def test_zero_deadline(self):
        """Test with zero-day deadline (same day requirement)."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-01-15",
            "reference_date": "2024-01-15",
            "deadline_days": 0
        })
        self.assertIn("COMPLIANT", result)
    
    def test_month_boundary(self):
        """Test compliance check crossing month boundary."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-02-05",
            "reference_date": "2024-01-25",
            "deadline_days": 15
        })
        self.assertIn("COMPLIANT", result)
        self.assertIn("11 days after reference date", result)
    
    def test_year_boundary(self):
        """Test compliance check crossing year boundary."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-01-10",
            "reference_date": "2023-12-20",
            "deadline_days": 30
        })
        self.assertIn("COMPLIANT", result)
        self.assertIn("21 days after reference date", result)
    
    def test_invalid_event_date_format(self):
        """Test error handling for invalid event date format."""
        result = check_policy_compliance.invoke({
            "event_date": "01/20/2024",
            "reference_date": "2024-01-15",
            "deadline_days": 30
        })
        self.assertIn("Error", result)
        self.assertIn("Invalid event_date format", result)
    
    def test_invalid_reference_date_format(self):
        """Test error handling for invalid reference date format."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-01-20",
            "reference_date": "15-01-2024",
            "deadline_days": 30
        })
        self.assertIn("Error", result)
        self.assertIn("Invalid reference_date format", result)
    
    def test_invalid_deadline_days_string(self):
        """Test error handling for non-integer deadline_days."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-01-20",
            "reference_date": "2024-01-15",
            "deadline_days": "thirty"
        })
        self.assertIn("Error", result)
        self.assertIn("must be an integer", result)
    
    def test_negative_deadline_days(self):
        """Test error handling for negative deadline_days."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-01-20",
            "reference_date": "2024-01-15",
            "deadline_days": -5
        })
        self.assertIn("Error", result)
        self.assertIn("must be positive", result)
    
    def test_missing_event_date(self):
        """Test error handling for missing event date."""
        result = check_policy_compliance.invoke({
            "event_date": "",
            "reference_date": "2024-01-15",
            "deadline_days": 30
        })
        self.assertIn("Error", result)
        self.assertIn("required", result)
    
    def test_missing_reference_date(self):
        """Test error handling for missing reference date."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-01-20",
            "reference_date": "",
            "deadline_days": 30
        })
        self.assertIn("Error", result)
        self.assertIn("required", result)
    
    def test_missing_deadline_days(self):
        """Test error handling for missing deadline_days."""
        result = check_policy_compliance.invoke({
            "event_date": "2024-01-20",
            "reference_date": "2024-01-15",
            "deadline_days": None
        })
        self.assertIn("Error", result)
        self.assertIn("required", result)


def run_all_tests():
    """Run all test suites and display results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCalculateTimelineDuration))
    suite.addTests(loader.loadTestsFromTestCase(TestCalculateBusinessDays))
    suite.addTests(loader.loadTestsFromTestCase(TestCheckPolicyCompliance))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    # Run all tests
    result = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
