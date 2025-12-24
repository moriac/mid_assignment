"""
MCP Date/Time Calculation Tools for Insurance Claim Analysis.

This module provides LangChain-compatible tools for performing date and time
calculations specific to insurance claim processing and compliance verification.
"""

from datetime import datetime, timedelta
from typing import Optional
from langchain.tools import tool


@tool
def calculate_timeline_duration(start_datetime: str, end_datetime: str) -> str:
    """Calculate precise duration between two timestamps.
    
    This tool calculates the exact time duration between two datetime points,
    returning a human-readable breakdown of days, hours, and minutes.
    
    Use this tool when user asks about:
    - "how long", "how much time", "time between", "duration", "elapsed time"
    - "time from X to Y", "how many days and hours"
    - "timeline", "time span", "period between"
    - "incident duration", "claim processing time"
    
    Args:
        start_datetime: Start timestamp in format "YYYY-MM-DD HH:MM:SS"
                       Example: "2024-01-15 09:30:00"
        end_datetime: End timestamp in format "YYYY-MM-DD HH:MM:SS"
                     Example: "2024-01-18 14:45:00"
    
    Returns:
        str: Human-readable duration string with breakdown of days, hours, minutes.
             Example: "Duration: 3 days, 5 hours, 15 minutes (Total: 77.25 hours)"
             
    Example usage:
        >>> calculate_timeline_duration("2024-01-15 09:00:00", "2024-01-18 14:30:00")
        "Duration: 3 days, 5 hours, 30 minutes (Total: 77.50 hours)"
        
        When to invoke:
        - User: "How long was the claim open from Jan 15 9am to Jan 18 2:30pm?"
        - User: "What's the duration between incident and report?"
        - User: "Calculate time elapsed from start to end"
    """
    try:
        # Validate inputs
        if not start_datetime or not end_datetime:
            return "Error: Both start_datetime and end_datetime are required."
        
        # Parse datetime strings
        try:
            start_dt = datetime.strptime(start_datetime.strip(), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return f"Error: Invalid start_datetime format '{start_datetime}'. Required format: 'YYYY-MM-DD HH:MM:SS' (e.g., '2024-01-15 09:30:00')"
        
        try:
            end_dt = datetime.strptime(end_datetime.strip(), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return f"Error: Invalid end_datetime format '{end_datetime}'. Required format: 'YYYY-MM-DD HH:MM:SS' (e.g., '2024-01-18 14:45:00')"
        
        # Check if end is before start
        if end_dt < start_dt:
            return f"Error: End datetime ({end_datetime}) is before start datetime ({start_datetime}). Please ensure end time is after start time."
        
        # Calculate duration
        duration = end_dt - start_dt
        
        # Extract components
        total_seconds = int(duration.total_seconds())
        days = duration.days
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        total_hours = duration.total_seconds() / 3600
        
        # Format response
        result = f"Duration: {days} days, {hours} hours, {minutes} minutes (Total: {total_hours:.2f} hours)"
        
        return result
        
    except Exception as e:
        return f"Error calculating duration: {str(e)}"


@tool
def calculate_business_days(start_date: str, end_date: str) -> str:
    """Calculate business days (excluding weekends) between two dates.
    
    This tool counts the number of business days (Monday-Friday) between two dates,
    providing a breakdown of calendar days, business days, and weekend days.
    
    Use this tool when user asks about:
    - "business days", "working days", "weekdays", "weekdays only"
    - "excluding weekends", "not counting weekends", "Monday through Friday"
    - "work days", "business time", "operational days"
    - "claim processing business days", "turnaround time in business days"
    
    Args:
        start_date: Start date in format "YYYY-MM-DD"
                   Example: "2024-01-15"
        end_date: End date in format "YYYY-MM-DD"
                 Example: "2024-01-25"
    
    Returns:
        str: Detailed breakdown of business days, calendar days, and weekend days.
             Example: "Business days: 8, Calendar days: 10, Weekend days: 2"
             
    Example usage:
        >>> calculate_business_days("2024-01-15", "2024-01-25")
        "Business days: 8, Calendar days: 10, Weekend days: 2 (from 2024-01-15 to 2024-01-25)"
        
        When to invoke:
        - User: "How many business days between Jan 15 and Jan 25?"
        - User: "Calculate working days excluding weekends"
        - User: "What's the business day count for claim processing?"
    """
    try:
        # Validate inputs
        if not start_date or not end_date:
            return "Error: Both start_date and end_date are required."
        
        # Parse date strings
        try:
            start_dt = datetime.strptime(start_date.strip(), "%Y-%m-%d")
        except ValueError:
            return f"Error: Invalid start_date format '{start_date}'. Required format: 'YYYY-MM-DD' (e.g., '2024-01-15')"
        
        try:
            end_dt = datetime.strptime(end_date.strip(), "%Y-%m-%d")
        except ValueError:
            return f"Error: Invalid end_date format '{end_date}'. Required format: 'YYYY-MM-DD' (e.g., '2024-01-25')"
        
        # Check if end is before start
        if end_dt < start_dt:
            return f"Error: End date ({end_date}) is before start date ({start_date}). Please ensure end date is after start date."
        
        # Calculate total calendar days (inclusive)
        calendar_days = (end_dt - start_dt).days + 1
        
        # Count business days
        business_days = 0
        current_date = start_dt
        
        while current_date <= end_dt:
            # Monday = 0, Sunday = 6
            if current_date.weekday() < 5:  # Monday to Friday
                business_days += 1
            current_date += timedelta(days=1)
        
        # Calculate weekend days
        weekend_days = calendar_days - business_days
        
        # Format response
        result = (f"Business days: {business_days}, "
                 f"Calendar days: {calendar_days}, "
                 f"Weekend days: {weekend_days} "
                 f"(from {start_date} to {end_date})")
        
        return result
        
    except Exception as e:
        return f"Error calculating business days: {str(e)}"


@tool
def check_policy_compliance(event_date: str, reference_date: str, deadline_days: int) -> str:
    """Check if an event occurred within required policy timeframe.
    
    This tool verifies compliance by checking if an event date falls within
    a specified number of days from a reference date. Useful for validating
    claim filing deadlines, notification requirements, and policy compliance.
    
    Use this tool when user asks about:
    - "check deadline", "verify compliance", "within timeframe", "meets requirement"
    - "policy requirement", "deadline compliance", "timely filing"
    - "reported on time", "within X days", "before deadline"
    - "claim filing deadline", "notification requirement", "compliance check"
    
    Args:
        event_date: The date of the event to check in format "YYYY-MM-DD"
                   Example: "2024-01-20"
        reference_date: The reference date (e.g., incident date) in format "YYYY-MM-DD"
                       Example: "2024-01-15"
        deadline_days: Maximum allowed days between reference and event (integer)
                      Example: 30
    
    Returns:
        str: Compliance status with detailed analysis including whether compliant,
             actual days difference, and deadline information.
             Example: "COMPLIANT: Event occurred 5 days after reference date. Deadline: 30 days. Status: Within deadline (25 days remaining)"
             
    Example usage:
        >>> check_policy_compliance("2024-01-20", "2024-01-15", 30)
        "COMPLIANT: Event occurred 5 days after reference date. Deadline: 30 days. Status: Within deadline (25 days remaining)"
        
        When to invoke:
        - User: "Was the claim filed within 30 days of the incident?"
        - User: "Check if notification deadline was met"
        - User: "Verify compliance with reporting timeframe"
    """
    try:
        # Validate inputs
        if not event_date or not reference_date:
            return "Error: Both event_date and reference_date are required."
        
        if deadline_days is None:
            return "Error: deadline_days is required."
        
        # Validate deadline_days is an integer
        try:
            deadline_days = int(deadline_days)
        except (ValueError, TypeError):
            return f"Error: deadline_days must be an integer, got '{deadline_days}'"
        
        if deadline_days < 0:
            return f"Error: deadline_days must be positive, got {deadline_days}"
        
        # Parse date strings
        try:
            event_dt = datetime.strptime(event_date.strip(), "%Y-%m-%d")
        except ValueError:
            return f"Error: Invalid event_date format '{event_date}'. Required format: 'YYYY-MM-DD' (e.g., '2024-01-20')"
        
        try:
            reference_dt = datetime.strptime(reference_date.strip(), "%Y-%m-%d")
        except ValueError:
            return f"Error: Invalid reference_date format '{reference_date}'. Required format: 'YYYY-MM-DD' (e.g., '2024-01-15')"
        
        # Calculate difference
        days_difference = (event_dt - reference_dt).days
        
        # Determine compliance
        if days_difference < 0:
            # Event before reference
            result = (f"INVALID: Event date ({event_date}) is {abs(days_difference)} days "
                     f"BEFORE reference date ({reference_date}). "
                     f"Event should occur after reference date.")
        elif days_difference <= deadline_days:
            # Compliant
            days_remaining = deadline_days - days_difference
            result = (f"COMPLIANT: Event occurred {days_difference} days after reference date. "
                     f"Deadline: {deadline_days} days. "
                     f"Status: Within deadline ({days_remaining} days remaining)")
        else:
            # Non-compliant
            days_overdue = days_difference - deadline_days
            result = (f"NON-COMPLIANT: Event occurred {days_difference} days after reference date. "
                     f"Deadline: {deadline_days} days. "
                     f"Status: EXCEEDED deadline by {days_overdue} days")
        
        return result
        
    except Exception as e:
        return f"Error checking policy compliance: {str(e)}"
