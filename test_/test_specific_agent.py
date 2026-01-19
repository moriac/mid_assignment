"""
Test file for SpecificTaskExpertAgent.process_specific_question method
Uses regex to validate agent responses contain expected information.
"""

import re
import pytest
from unittest.mock import patch, MagicMock
from specific_task_expert_agent import SpecificTaskExpertAgent


class TestProcessSpecificQuestionRegex:
    """Tests for process_specific_question using regex validation."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mocked agent to avoid external API calls during testing."""
        with patch.object(SpecificTaskExpertAgent, '__init__', lambda x, **kwargs: None):
            agent = SpecificTaskExpertAgent()
            agent.llm = MagicMock()
            agent.llm_with_tools = MagicMock()
            agent.date_tools = []
            agent.use_hierarchical_retrieval = False
            agent.hierarchical_retriever = None
            return agent

    def test_claim_date_response_contains_date_pattern(self, mock_agent):
        """Test that claim date response matches expected date regex pattern."""
        # Simulate the expected response
        expected_response = "The claim was filed on March 15, 2024 at 11:00 AM."
        
        mock_response = MagicMock()
        mock_response.content = expected_response
        mock_response.tool_calls = None
        mock_agent.llm_with_tools.invoke.return_value = mock_response
        
        result = mock_agent.process_specific_question("What is the claim date?")
        
        # Regex pattern for "March 15, 2024"
        date_pattern = r"March\s+15,?\s*2024"
        assert re.search(date_pattern, result), f"Expected date pattern not found in: {result}"

    def test_claim_date_response_contains_time_pattern(self, mock_agent):
        """Test that claim date response matches expected time regex pattern."""
        expected_response = "The claim was filed on March 15, 2024 at 11:00 AM."
        
        mock_response = MagicMock()
        mock_response.content = expected_response
        mock_response.tool_calls = None
        mock_agent.llm_with_tools.invoke.return_value = mock_response
        
        result = mock_agent.process_specific_question("What is the claim date?")
        
        # Regex pattern for time "11:00 AM"
        time_pattern = r"11:00\s*AM"
        assert re.search(time_pattern, result, re.IGNORECASE), f"Expected time pattern not found in: {result}"

    def test_claim_date_response_full_pattern(self, mock_agent):
        """Test that claim date response matches full expected pattern."""
        expected_response = "The claim was filed on March 15, 2024 at 11:00 AM."
        
        mock_response = MagicMock()
        mock_response.content = expected_response
        mock_response.tool_calls = None
        mock_agent.llm_with_tools.invoke.return_value = mock_response
        
        result = mock_agent.process_specific_question("What is the claim date?")
        
        # Full regex pattern for the complete response
        full_pattern = r"claim\s+was\s+filed\s+on\s+March\s+15,?\s*2024\s+at\s+11:00\s*AM"
        assert re.search(full_pattern, result, re.IGNORECASE), f"Expected full pattern not found in: {result}"

    def test_claim_date_flexible_date_format(self, mock_agent):
        """Test with flexible date format patterns (handles variations)."""
        expected_response = "The claim was filed on March 15, 2024 at 11:00 AM."
        
        mock_response = MagicMock()
        mock_response.content = expected_response
        mock_response.tool_calls = None
        mock_agent.llm_with_tools.invoke.return_value = mock_response
        
        result = mock_agent.process_specific_question("What is the claim date?")
        
        # Flexible patterns that match various date formats
        date_patterns = [
            r"March\s+15,?\s*2024",           # March 15, 2024 or March 15 2024
            r"03[/-]15[/-]2024",               # 03/15/2024 or 03-15-2024
            r"2024[/-]03[/-]15",               # 2024-03-15 or 2024/03/15
            r"15\s+March,?\s*2024",            # 15 March 2024
        ]
        
        matched = any(re.search(pattern, result, re.IGNORECASE) for pattern in date_patterns)
        assert matched, f"No expected date pattern found in: {result}"

    def test_claim_date_extracts_date_value(self, mock_agent):
        """Test extracting the actual date value from the response."""
        expected_response = "The claim was filed on March 15, 2024 at 11:00 AM."
        
        mock_response = MagicMock()
        mock_response.content = expected_response
        mock_response.tool_calls = None
        mock_agent.llm_with_tools.invoke.return_value = mock_response
        
        result = mock_agent.process_specific_question("What is the claim date?")
        
        # Extract date using regex groups
        date_pattern = r"(March\s+\d{1,2},?\s*\d{4})"
        match = re.search(date_pattern, result)
        
        assert match is not None, f"Could not extract date from: {result}"
        extracted_date = match.group(1)
        assert "March" in extracted_date
        assert "15" in extracted_date
        assert "2024" in extracted_date

    def test_claim_date_response_not_empty(self, mock_agent):
        """Test that the response is not empty."""
        expected_response = "The claim was filed on March 15, 2024 at 11:00 AM."
        
        mock_response = MagicMock()
        mock_response.content = expected_response
        mock_response.tool_calls = None
        mock_agent.llm_with_tools.invoke.return_value = mock_response
        
        result = mock_agent.process_specific_question("What is the claim date?")
        
        assert result is not None
        assert len(result.strip()) > 0
        assert not re.match(r"^\s*$", result)


class TestProcessSpecificQuestionRegexNegative:
    """Negative tests to ensure regex doesn't match incorrect responses."""

    @pytest.fixture
    def mock_agent(self):
        """Create a mocked agent."""
        with patch.object(SpecificTaskExpertAgent, '__init__', lambda x, **kwargs: None):
            agent = SpecificTaskExpertAgent()
            agent.llm = MagicMock()
            agent.llm_with_tools = MagicMock()
            agent.date_tools = []
            agent.use_hierarchical_retrieval = False
            agent.hierarchical_retriever = None
            return agent

    def test_wrong_date_does_not_match(self, mock_agent):
        """Test that wrong date does not match the expected pattern."""
        wrong_response = "The claim was filed on April 20, 2024 at 11:00 AM."
        
        mock_response = MagicMock()
        mock_response.content = wrong_response
        mock_response.tool_calls = None
        mock_agent.llm_with_tools.invoke.return_value = mock_response
        
        result = mock_agent.process_specific_question("What is the claim date?")
        
        # This should NOT match March 15, 2024
        correct_date_pattern = r"March\s+15,?\s*2024"
        assert not re.search(correct_date_pattern, result), "Wrong date should not match expected pattern"

    def test_wrong_time_does_not_match(self, mock_agent):
        """Test that wrong time does not match the expected pattern."""
        wrong_response = "The claim was filed on March 15, 2024 at 3:00 PM."
        
        mock_response = MagicMock()
        mock_response.content = wrong_response
        mock_response.tool_calls = None
        mock_agent.llm_with_tools.invoke.return_value = mock_response
        
        result = mock_agent.process_specific_question("What is the claim date?")
        
        # This should NOT match 11:00 AM
        correct_time_pattern = r"11:00\s*AM"
        assert not re.search(correct_time_pattern, result, re.IGNORECASE), "Wrong time should not match expected pattern"


# =============================================================================
# INTEGRATION TESTS - These call the REAL agent with actual LLM API calls
# =============================================================================

@pytest.mark.integration
class TestSpecificTaskExpertAgentIntegration:
    """
    Integration tests that call the REAL SpecificTaskExpertAgent.
    These tests require:
    - OPENAI_API_KEY environment variable set
    - ChromaDB with indexed data available
    
    Run with: pytest test_/test_specific_agent.py -v -m integration
    """

    @pytest.fixture(scope="class")
    def real_agent(self):
        """Create a real agent instance (called once per test class)."""
        import os
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set - skipping integration tests")
        
        try:
            agent = SpecificTaskExpertAgent(
                model_name="gpt-3.5-turbo",
                temperature=0,
                use_hierarchical_retrieval=True
            )
            return agent
        except Exception as e:
            pytest.skip(f"Could not initialize agent: {e}")

    def test_real_agent_claim_date_response_contains_date(self, real_agent):
        """
        REAL TEST: Call the actual agent and verify response contains a date.
        Expected answer: "The claim was filed on March 15, 2024 at 11:00 AM."
        """
        question = "What is the claim date?"
        
        # Call the REAL agent
        result = real_agent.process_specific_question(question)
        
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"Agent Response: {result}")
        print(f"{'='*60}\n")
        
        # Verify response is not empty
        assert result is not None, "Agent returned None"
        assert len(result.strip()) > 0, "Agent returned empty response"
        
        # Regex pattern for March 15, 2024 (flexible)
        date_pattern = r"March\s+15,?\s*2024"
        assert re.search(date_pattern, result, re.IGNORECASE), \
            f"Expected 'March 15, 2024' not found in response: {result}"

    def test_real_agent_claim_date_response_contains_time(self, real_agent):
        """
        REAL TEST: Call the actual agent and verify response contains the time.
        Expected answer: "The claim was filed on March 15, 2024 at 11:00 AM."
        """
        question = "What is the claim date?"
        
        # Call the REAL agent
        result = real_agent.process_specific_question(question)
        
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"Agent Response: {result}")
        print(f"{'='*60}\n")
        
        # Regex pattern for 11:00 AM
        time_pattern = r"11:00\s*AM"
        assert re.search(time_pattern, result, re.IGNORECASE), \
            f"Expected '11:00 AM' not found in response: {result}"

    def test_real_agent_claim_date_full_validation(self, real_agent):
        """
        REAL TEST: Full validation of claim date response.
        Expected answer: "The claim was filed on March 15, 2024 at 11:00 AM."
        """
        question = "What is the claim date?"
        
        # Call the REAL agent
        result = real_agent.process_specific_question(question)
        
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"Agent Response: {result}")
        print(f"{'='*60}\n")
        
        # Multiple regex validations
        validations = {
            "date_march_15_2024": r"March\s+15,?\s*2024",
            "time_11_00_am": r"11:00\s*AM",
            "contains_filed": r"filed",
        }
        
        failed_validations = []
        for name, pattern in validations.items():
            if not re.search(pattern, result, re.IGNORECASE):
                failed_validations.append(f"{name}: pattern '{pattern}' not found")
        
        assert len(failed_validations) == 0, \
            f"Validation failures in response '{result}':\n" + "\n".join(failed_validations)

    def test_real_agent_claim_date_extract_and_validate(self, real_agent):
        """
        REAL TEST: Extract date components and validate them individually.
        Expected answer: "The claim was filed on March 15, 2024 at 11:00 AM."
        """
        question = "What is the claim date?"
        
        # Call the REAL agent
        result = real_agent.process_specific_question(question)
        
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"Agent Response: {result}")
        print(f"{'='*60}\n")
        
        # Extract date pattern
        date_pattern = r"(March)\s+(\d{1,2}),?\s*(\d{4})"
        date_match = re.search(date_pattern, result, re.IGNORECASE)
        
        assert date_match is not None, f"Could not extract date from: {result}"
        
        month = date_match.group(1)
        day = date_match.group(2)
        year = date_match.group(3)
        
        # Validate extracted components
        assert month.lower() == "march", f"Expected month 'March', got '{month}'"
        assert day == "15", f"Expected day '15', got '{day}'"
        assert year == "2024", f"Expected year '2024', got '{year}'"
        
        # Extract and validate time
        time_pattern = r"(\d{1,2}):(\d{2})\s*(AM|PM)"
        time_match = re.search(time_pattern, result, re.IGNORECASE)
        
        assert time_match is not None, f"Could not extract time from: {result}"
        
        hour = time_match.group(1)
        minute = time_match.group(2)
        period = time_match.group(3)
        
        assert hour == "11", f"Expected hour '11', got '{hour}'"
        assert minute == "00", f"Expected minute '00', got '{minute}'"
        assert period.upper() == "AM", f"Expected 'AM', got '{period}'"

    # =========================================================================
    # CLAIM AMOUNT TESTS
    # Expected answer: "The claim amount is $387,500.00."
    # =========================================================================

    def test_real_agent_claim_amount_response_contains_amount(self, real_agent):
        """
        REAL TEST: Call the actual agent and verify response contains the claim amount.
        Expected answer: "The claim amount is $387,500.00."
        """
        question = "What is the claim amount?"
        
        # Call the REAL agent
        result = real_agent.process_specific_question(question)
        
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"Agent Response: {result}")
        print(f"{'='*60}\n")
        
        # Verify response is not empty
        assert result is not None, "Agent returned None"
        assert len(result.strip()) > 0, "Agent returned empty response"
        
        # Regex pattern for $387,500 (with optional decimal and cents)
        amount_pattern = r"\$?387[,.]?500"
        assert re.search(amount_pattern, result, re.IGNORECASE), \
            f"Expected '$387,500' not found in response: {result}"

    def test_real_agent_claim_amount_with_currency_symbol(self, real_agent):
        """
        REAL TEST: Verify the claim amount includes the dollar sign.
        Expected answer: "The claim amount is $387,500.00."
        """
        question = "What is the claim amount?"
        
        # Call the REAL agent
        result = real_agent.process_specific_question(question)
        
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"Agent Response: {result}")
        print(f"{'='*60}\n")
        
        # Regex pattern for dollar amount with $ symbol
        currency_pattern = r"\$\s*387[,.]?500"
        assert re.search(currency_pattern, result), \
            f"Expected dollar amount with '$' symbol not found in response: {result}"

    def test_real_agent_claim_amount_full_validation(self, real_agent):
        """
        REAL TEST: Full validation of claim amount response.
        Expected answer: "The claim amount is $387,500.00."
        """
        question = "What is the claim amount?"
        
        # Call the REAL agent
        result = real_agent.process_specific_question(question)
        
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"Agent Response: {result}")
        print(f"{'='*60}\n")
        
        # Multiple regex validations
        validations = {
            "amount_387500": r"387[,.]?500",
            "currency_symbol": r"\$",
            "contains_claim_or_amount": r"(claim|amount|total)",
        }
        
        failed_validations = []
        for name, pattern in validations.items():
            if not re.search(pattern, result, re.IGNORECASE):
                failed_validations.append(f"{name}: pattern '{pattern}' not found")
        
        assert len(failed_validations) == 0, \
            f"Validation failures in response '{result}':\n" + "\n".join(failed_validations)

    def test_real_agent_claim_amount_extract_and_validate(self, real_agent):
        """
        REAL TEST: Extract the monetary value and validate components.
        Expected answer: "The claim amount is $387,500.00."
        """
        question = "What is the claim amount?"
        
        # Call the REAL agent
        result = real_agent.process_specific_question(question)
        
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"Agent Response: {result}")
        print(f"{'='*60}\n")
        
        # Extract monetary amount pattern: $387,500.00 or $387500 or $387,500
        money_pattern = r"\$\s*([\d,]+)(?:\.(\d{2}))?"
        money_match = re.search(money_pattern, result)
        
        assert money_match is not None, f"Could not extract monetary value from: {result}"
        
        # Get the whole number part (remove commas for comparison)
        whole_part = money_match.group(1).replace(",", "")
        cents_part = money_match.group(2) if money_match.group(2) else "00"
        
        # Validate extracted components
        assert whole_part == "387500", f"Expected whole part '387500', got '{whole_part}'"
        assert cents_part == "00", f"Expected cents '00', got '{cents_part}'"
        
        # Verify the numeric value
        extracted_value = float(f"{whole_part}.{cents_part}")
        assert extracted_value == 387500.00, f"Expected 387500.00, got {extracted_value}"

    def test_real_agent_claim_amount_flexible_formats(self, real_agent):
        """
        REAL TEST: Test with flexible amount format patterns.
        Expected answer: "The claim amount is $387,500.00."
        """
        question = "What is the claim amount?"
        
        # Call the REAL agent
        result = real_agent.process_specific_question(question)
        
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"Agent Response: {result}")
        print(f"{'='*60}\n")
        
        # Flexible patterns that match various money formats
        amount_patterns = [
            r"\$387,500\.00",        # $387,500.00
            r"\$387,500",            # $387,500
            r"\$387500\.00",         # $387500.00
            r"\$387500",             # $387500
            r"387,500\s*dollars",    # 387,500 dollars
            r"387500\s*dollars",     # 387500 dollars
        ]
        
        matched = any(re.search(pattern, result, re.IGNORECASE) for pattern in amount_patterns)
        assert matched, f"No expected amount pattern found in: {result}"