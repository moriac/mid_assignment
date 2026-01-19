"""
LLM Evaluation Tests for SpecificTaskExpertAgent
================================================
Uses LLM-as-a-judge approach to evaluate agent responses against ground truth answers.
A different LLM model evaluates the accuracy of the agent's responses.
"""

import os
import sys
import pytest
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import the agent to test
from specific_task_expert_agent import SpecificTaskExpertAgent


# ============================================================================
# TEST DATA: Questions and Ground Truth Answers
# ============================================================================
# Add more test cases here as needed

TEST_CASES = [
    {
        "id": "incident_reported_date",
        "question": "When was the incident reported?",
        "ground_truth": "The incident was reported on March 15, 2024, at 11:00 AM."
    },
    {
        "id": "days_elapsed_incident_to_claim",
        "question": "How many days elapsed between the incident date and when the claim was filed?",
        "ground_truth": "The exact duration between the incident date and when the claim was filed is 3 days, 8 hours, and 13 minutes, totaling 80.22 hours."
    },
    {
        "id": "water_pooling_discovery_time",
        "question": "According to the chronological event timeline, at what precise time did the morning shift supervisor discover water pooling in the basement mechanical room and second‑floor production area on March 12, 2024?",
        "ground_truth": "6:30 AM on March 12, 2024"
    },
    # Add more test cases below:
    # {
    #     "id": "claim_amount",
    #     "question": "What is the claim amount?",
    #     "ground_truth": "The claim amount is $387,500.00."
    # },
]


class LLMJudge:
    """
    LLM-as-a-Judge evaluator that compares agent responses against ground truth.
    Uses a different model than the agent being tested for unbiased evaluation.
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        Initialize the LLM Judge with a specified model.
        
        Args:
            model_name: The model to use for evaluation (should differ from agent's model)
        """
        self.llm = ChatOpenAI(model=model_name, temperature=0)
    
    def evaluate(self, question: str, agent_answer: str, ground_truth: str) -> dict:
        """
        Evaluate the agent's answer against the ground truth.
        
        Args:
            question: The original question asked
            agent_answer: The answer provided by the agent
            ground_truth: The correct/expected answer
            
        Returns:
            Dictionary containing:
                - score: Integer from 0 to 100 representing accuracy percentage
                - reasoning: Explanation of the score
        """
        system_prompt = """You are an expert evaluator assessing the accuracy of AI-generated answers.
Your task is to compare an agent's answer against a ground truth answer and provide a score.

SCORING GUIDELINES:
- 100%: Perfect match - all key information is correct and complete
- 80-99%: Excellent - minor differences in wording but all facts are correct
- 60-79%: Good - most key information is correct, minor omissions or slight inaccuracies
- 40-59%: Partial - some correct information but significant omissions or errors
- 20-39%: Poor - few correct elements, major errors or missing information
- 0-19%: Incorrect - answer is wrong, irrelevant, or completely misses the point

EVALUATION CRITERIA:
1. Factual accuracy (dates, times, numbers, names must match)
2. Completeness (all key information from ground truth should be present)
3. Relevance (answer should address the question asked)

IMPORTANT: Focus on semantic correctness, not exact wording. Different phrasing is acceptable if the meaning is the same.

You MUST respond in the following exact format:
SCORE: [number from 0 to 100]
REASONING: [your explanation]"""

        evaluation_prompt = f"""Question: {question}

Ground Truth Answer: {ground_truth}

Agent's Answer: {agent_answer}

Please evaluate the agent's answer against the ground truth and provide your score and reasoning."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=evaluation_prompt)
        ]
        
        response = self.llm.invoke(messages)
        
        # Parse the response
        return self._parse_evaluation_response(response.content)
    
    def _parse_evaluation_response(self, response_text: str) -> dict:
        """
        Parse the LLM judge's response to extract score and reasoning.
        
        Args:
            response_text: Raw response from the LLM judge
            
        Returns:
            Dictionary with 'score' and 'reasoning' keys
        """
        lines = response_text.strip().split('\n')
        score = 0
        reasoning = ""
        
        for i, line in enumerate(lines):
            if line.upper().startswith('SCORE:'):
                # Extract numeric score
                score_text = line.split(':', 1)[1].strip()
                # Remove any % sign and extract the number
                score_text = score_text.replace('%', '').strip()
                try:
                    score = int(float(score_text))
                    score = max(0, min(100, score))  # Clamp between 0 and 100
                except ValueError:
                    score = 0
            elif line.upper().startswith('REASONING:'):
                # Get reasoning (may span multiple lines)
                reasoning = line.split(':', 1)[1].strip()
                # Include any remaining lines as part of reasoning
                if i + 1 < len(lines):
                    reasoning += ' ' + ' '.join(lines[i + 1:])
                break
        
        return {
            "score": score,
            "reasoning": reasoning.strip()
        }


class TestLLMEvaluation:
    """
    Test class for LLM-based evaluation of SpecificTaskExpertAgent responses.
    """
    
    @pytest.fixture(scope="class")
    def agent(self):
        """Create the agent to be tested."""
        return SpecificTaskExpertAgent(
            model_name="gpt-3.5-turbo",
            temperature=0,
            use_hierarchical_retrieval=True
        )
    
    @pytest.fixture(scope="class")
    def judge(self):
        """Create the LLM judge using a different model."""
        # Using gpt-4o-mini as the judge (different from agent's gpt-3.5-turbo)
        return LLMJudge(model_name="gpt-4o-mini")
    
    @pytest.mark.parametrize("test_case", TEST_CASES, ids=[tc["id"] for tc in TEST_CASES])
    def test_agent_response_accuracy(self, agent, judge, test_case):
        """
        Test that agent responses meet accuracy threshold when evaluated by LLM judge.
        
        This test:
        1. Asks the agent a question
        2. Gets the agent's response
        3. Uses an LLM judge to compare against ground truth
        4. Asserts the score meets the minimum threshold (70%)
        """
        question = test_case["question"]
        ground_truth = test_case["ground_truth"]
        min_score_threshold = 70  # Minimum acceptable score (70%)
        
        # Step 1: Get agent's answer
        print(f"\n{'='*60}")
        print(f"Test Case: {test_case['id']}")
        print(f"{'='*60}")
        print(f"Question: {question}")
        
        agent_answer = agent.process_specific_question(question)
        print(f"\nAgent's Answer: {agent_answer}")
        print(f"Ground Truth: {ground_truth}")
        
        # Step 2: Evaluate with LLM judge
        evaluation = judge.evaluate(question, agent_answer, ground_truth)
        
        print(f"\n--- LLM Judge Evaluation ---")
        print(f"Score: {evaluation['score']}%")
        print(f"Reasoning: {evaluation['reasoning']}")
        print(f"{'='*60}\n")
        
        # Step 3: Assert score meets threshold
        assert evaluation["score"] >= min_score_threshold, (
            f"Agent response accuracy ({evaluation['score']}%) below threshold ({min_score_threshold}%).\n"
            f"Question: {question}\n"
            f"Agent Answer: {agent_answer}\n"
            f"Ground Truth: {ground_truth}\n"
            f"Judge Reasoning: {evaluation['reasoning']}"
        )


class TestLLMEvaluationDetailed:
    """
    Detailed test class with individual tests for each question.
    Useful for granular test reporting and CI/CD integration.
    """
    
    @pytest.fixture(scope="class")
    def agent(self):
        """Create the agent to be tested."""
        return SpecificTaskExpertAgent(
            model_name="gpt-3.5-turbo",
            temperature=0,
            use_hierarchical_retrieval=True
        )
    
    @pytest.fixture(scope="class")
    def judge(self):
        """Create the LLM judge using a different model."""
        return LLMJudge(model_name="gpt-4o-mini")
    
    def test_incident_reported_date(self, agent, judge):
        """Test: When was the incident reported?"""
        question = "When was the incident reported?"
        ground_truth = "The incident was reported on March 15, 2024, at 11:00 AM."
        min_score_threshold = 70
        
        # Get agent's answer
        agent_answer = agent.process_specific_question(question)
        
        # Evaluate with LLM judge
        evaluation = judge.evaluate(question, agent_answer, ground_truth)
        
        print(f"\n--- Test: Incident Reported Date ---")
        print(f"Question: {question}")
        print(f"Agent Answer: {agent_answer}")
        print(f"Ground Truth: {ground_truth}")
        print(f"Score: {evaluation['score']}%")
        print(f"Reasoning: {evaluation['reasoning']}")
        
        assert evaluation["score"] >= min_score_threshold, (
            f"Score {evaluation['score']}% below threshold {min_score_threshold}%"
        )


# ============================================================================
# Standalone Evaluation Function (for use outside pytest)
# ============================================================================

def run_llm_evaluation(
    question: str,
    ground_truth: str,
    agent_model: str = "gpt-3.5-turbo",
    judge_model: str = "gpt-4o-mini",
    verbose: bool = True
) -> dict:
    """
    Run a single LLM evaluation test.
    
    Args:
        question: The question to ask the agent
        ground_truth: The expected correct answer
        agent_model: Model for the agent being tested
        judge_model: Model for the LLM judge
        verbose: Whether to print detailed output
        
    Returns:
        Dictionary containing evaluation results
    """
    # Initialize agent and judge
    agent = SpecificTaskExpertAgent(
        model_name=agent_model,
        temperature=0,
        use_hierarchical_retrieval=True
    )
    judge = LLMJudge(model_name=judge_model)
    
    # Get agent's answer
    agent_answer = agent.process_specific_question(question)
    
    # Evaluate
    evaluation = judge.evaluate(question, agent_answer, ground_truth)
    
    result = {
        "question": question,
        "ground_truth": ground_truth,
        "agent_answer": agent_answer,
        "score": evaluation["score"],
        "reasoning": evaluation["reasoning"],
        "passed": evaluation["score"] >= 70
    }
    
    if verbose:
        print(f"\n{'='*60}")
        print("LLM EVALUATION RESULTS")
        print(f"{'='*60}")
        print(f"Question: {question}")
        print(f"Ground Truth: {ground_truth}")
        print(f"Agent Answer: {agent_answer}")
        print(f"\n--- Judge Evaluation ---")
        print(f"Score: {evaluation['score']}%")
        print(f"Reasoning: {evaluation['reasoning']}")
        print(f"Status: {'✅ PASSED' if result['passed'] else '❌ FAILED'}")
        print(f"{'='*60}\n")
    
    return result


def run_all_evaluations(verbose: bool = True) -> list:
    """
    Run all test cases and return results.
    
    Args:
        verbose: Whether to print detailed output
        
    Returns:
        List of evaluation results for all test cases
    """
    results = []
    
    for test_case in TEST_CASES:
        result = run_llm_evaluation(
            question=test_case["question"],
            ground_truth=test_case["ground_truth"],
            verbose=verbose
        )
        result["test_id"] = test_case["id"]
        results.append(result)
    
    # Print summary
    if verbose:
        passed = sum(1 for r in results if r["passed"])
        total = len(results)
        print(f"\n{'='*60}")
        print(f"EVALUATION SUMMARY: {passed}/{total} tests passed")
        print(f"{'='*60}")
        for r in results:
            status = "✅" if r["passed"] else "❌"
            print(f"{status} {r['test_id']}: {r['score']}%")
    
    return results


if __name__ == "__main__":
    # Run evaluations when executed directly
    print("Running LLM Evaluation Tests...")
    print("=" * 60)
    
    # Run all test cases
    results = run_all_evaluations(verbose=True)
    
    # Exit with appropriate code
    all_passed = all(r["passed"] for r in results)
    exit(0 if all_passed else 1)
