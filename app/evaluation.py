"""
Evaluation pipeline for assessing and improving answer quality.
Implements metrics, test cases, and continuous improvement mechanisms.
"""

import asyncio
import statistics
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# Make logfire optional
try:
    import logfire
except ImportError:
    # Create a dummy logfire module with no-op methods
    class DummyLogfire:
        def span(self, *args, **kwargs):
            from contextlib import contextmanager

            @contextmanager
            def dummy_context():
                yield

            return dummy_context()

        def info(self, *args, **kwargs):
            pass

    logfire = DummyLogfire()

from .llm_service import LLMService
from .models import Patient, Question


class EvaluationMetric(Enum):
    """Types of evaluation metrics."""

    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    MEDICAL_CORRECTNESS = "medical_correctness"
    RESPONSE_TIME = "response_time"
    CONFIDENCE_CALIBRATION = "confidence_calibration"


class TestCase(BaseModel):
    """Test case for evaluation."""

    patient: Patient
    question: Question
    expected_answer: str | bool
    acceptable_variations: list[str | bool] | None = None
    reasoning: str
    tags: list[str] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    """Result of a single evaluation."""

    test_case_id: str
    question_key: str
    expected: str | bool
    actual: str | bool
    confidence: float
    is_correct: bool
    is_acceptable: bool
    reasoning_quality: float
    response_time_ms: float
    error: str | None = None


class EvaluationReport(BaseModel):
    """Comprehensive evaluation report."""

    timestamp: datetime
    total_tests: int
    passed: int
    failed: int
    accuracy: float
    average_confidence: float
    confidence_calibration_error: float
    average_response_time_ms: float
    results_by_category: dict[str, dict[str, float]]
    problem_areas: list[str]
    recommendations: list[str]


class EvaluationPipeline:
    """Pipeline for evaluating and improving answer generation."""

    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService()
        self.test_cases = self._load_test_cases()
        self.historical_results: list[EvaluationResult] = []

    def _load_test_cases(self) -> list[TestCase]:
        """Load comprehensive test cases for evaluation."""
        # Sample test cases - in production, these would be loaded from a database or file
        test_cases = [
            # BMI Calculations
            TestCase(
                patient=Patient(
                    first_name="Test",
                    last_name="Patient1",
                    date_of_birth="1975-01-01",
                    gender="Male",
                    prescription={
                        "medication": "Zepbound",
                        "dosage": "10 mg",
                        "frequency": "once weekly",
                        "duration": "ongoing",
                    },
                    visit_notes=[
                        "Patient height: 170 cm, weight: 95 kg",
                        "BMI calculated at 32.9 kg/m²",
                    ],
                ),
                question=Question(
                    type="text",
                    key="bmi",
                    content="What is the patient's body mass index (BMI) in kilograms per square meter (kg/m2)",
                ),
                expected_answer="32.9",
                acceptable_variations=["32.9 kg/m²", "33", "32.87"],
                reasoning="BMI is explicitly stated in visit notes",
                tags=["bmi", "calculation", "text_answer"],
            ),
            # Age Calculation
            TestCase(
                patient=Patient(
                    first_name="Test",
                    last_name="Patient2",
                    date_of_birth="1990-06-15",
                    gender="Female",
                    prescription={
                        "medication": "Zepbound",
                        "dosage": "5 mg",
                        "frequency": "once weekly",
                        "duration": "3 months",
                    },
                    visit_notes=["Patient presents for weight management consultation"],
                ),
                question=Question(
                    type="text",
                    key="age",
                    content="What is the patient's age in years?",
                ),
                expected_answer="34",  # Assuming current date is in 2024
                acceptable_variations=["34 years", "34"],
                reasoning="Age calculated from date of birth",
                tags=["age", "calculation", "demographics"],
            ),
            # Boolean Question - Lifestyle Modifications
            TestCase(
                patient=Patient(
                    first_name="Test",
                    last_name="Patient3",
                    date_of_birth="1980-03-20",
                    gender="Male",
                    prescription={
                        "medication": "Zepbound",
                        "dosage": "15 mg",
                        "frequency": "once weekly",
                        "duration": "ongoing",
                    },
                    visit_notes=[
                        "Patient has been on structured diet and exercise program for 8 months",
                        "Regular follow-ups with nutritionist and personal trainer",
                        "Compliant with lifestyle modification protocol",
                    ],
                ),
                question=Question(
                    type="boolean",
                    key="antiobesity_wt_mgmt_6m",
                    content="Has the patient participated in a comprehensive weight-management program (diet, exercise, follow-up) for at least 6 months prior to drug therapy?",
                ),
                expected_answer=True,
                reasoning="Visit notes clearly indicate 8 months of structured diet and exercise program",
                tags=["boolean", "lifestyle", "prerequisites"],
            ),
            # Continuation of Therapy
            TestCase(
                patient=Patient(
                    first_name="Test",
                    last_name="Patient4",
                    date_of_birth="1985-11-10",
                    gender="Female",
                    prescription={
                        "medication": "Zepbound",
                        "dosage": "10 mg",
                        "frequency": "once weekly",
                        "duration": "ongoing",
                    },
                    visit_notes=[
                        "Patient on Zepbound for 4 months",
                        "Started at 185 lbs, current weight 165 lbs",
                        "Weight loss of 20 lbs represents 10.8% reduction from baseline",
                    ],
                ),
                question=Question(
                    type="boolean",
                    key="cont_wl_gt5percent",
                    content="Has the patient had a weight loss of more than or equal to 5% of baseline body weight?",
                ),
                expected_answer=True,
                reasoning="Patient has lost 10.8% of baseline weight, exceeding the 5% threshold",
                tags=["boolean", "weight_loss", "continuation"],
            ),
            # Comorbidity Assessment
            TestCase(
                patient=Patient(
                    first_name="Test",
                    last_name="Patient5",
                    date_of_birth="1978-07-22",
                    gender="Male",
                    prescription={
                        "medication": "Zepbound",
                        "dosage": "5 mg",
                        "frequency": "once weekly",
                        "duration": "new",
                    },
                    visit_notes=[
                        "BMI: 28.5 kg/m²",
                        "Diagnosed with Type 2 Diabetes Mellitus",
                        "Hypertension - controlled with medication",
                        "Dyslipidemia - LDL 165 mg/dL",
                    ],
                ),
                question=Question(
                    type="boolean",
                    key="antiobesity_bmi_ge27_comorbid",
                    content="Does the patient have a BMI greater than or equal to 27 kg per square meter AND at least one weight-related comorbid condition?",
                ),
                expected_answer=True,
                reasoning="BMI is 28.5 (≥27) and patient has multiple comorbidities: diabetes, hypertension, dyslipidemia",
                tags=["boolean", "bmi", "comorbidity"],
            ),
        ]

        return test_cases

    async def evaluate_single_test(self, test_case: TestCase) -> EvaluationResult:
        """Evaluate a single test case."""
        start_time = datetime.now()

        try:
            # Generate answer
            answer = await self.llm_service.generate_answer_with_confidence(
                test_case.patient, test_case.question
            )

            # Calculate response time
            response_time_ms = (datetime.now() - start_time).total_seconds() * 1000

            # Check correctness
            is_correct = self._check_answer_correctness(
                answer.value, test_case.expected_answer, test_case.acceptable_variations
            )

            # Evaluate reasoning quality
            reasoning_quality = await self._evaluate_reasoning_quality(
                answer.reasoning, test_case.reasoning
            )

            return EvaluationResult(
                test_case_id=f"{test_case.question.key}_{id(test_case)}",
                question_key=test_case.question.key,
                expected=test_case.expected_answer,
                actual=answer.value,
                confidence=answer.confidence,
                is_correct=is_correct,
                is_acceptable=is_correct
                or (answer.value in (test_case.acceptable_variations or [])),
                reasoning_quality=reasoning_quality,
                response_time_ms=response_time_ms,
            )

        except Exception as e:
            return EvaluationResult(
                test_case_id=f"{test_case.question.key}_{id(test_case)}",
                question_key=test_case.question.key,
                expected=test_case.expected_answer,
                actual="",
                confidence=0.0,
                is_correct=False,
                is_acceptable=False,
                reasoning_quality=0.0,
                response_time_ms=(datetime.now() - start_time).total_seconds() * 1000,
                error=str(e),
            )

    def _check_answer_correctness(
        self, actual: Any, expected: Any, acceptable_variations: list[Any] | None = None
    ) -> bool:
        """Check if the answer is correct."""
        # Direct match
        if actual == expected:
            return True

        # Check acceptable variations
        if acceptable_variations and actual in acceptable_variations:
            return True

        # For text answers, check if the core value is present
        if isinstance(expected, str) and isinstance(actual, str):
            # Remove units and compare
            actual_clean = actual.replace("kg/m²", "").replace("years", "").strip()
            expected_clean = expected.replace("kg/m²", "").replace("years", "").strip()

            try:
                # Try numeric comparison for numbers
                if float(actual_clean) == float(expected_clean):
                    return True
            except ValueError:
                pass

        return False

    async def _evaluate_reasoning_quality(
        self, actual_reasoning: str, expected_reasoning: str
    ) -> float:
        """Evaluate the quality of reasoning (0.0 to 1.0)."""
        # Simple heuristic - in production, this could use another LLM call
        # or more sophisticated NLP techniques

        if not actual_reasoning:
            return 0.0

        quality_score = 1.0

        # Check for key elements
        key_elements = expected_reasoning.lower().split()
        actual_lower = actual_reasoning.lower()

        matched_elements = sum(1 for element in key_elements if element in actual_lower)
        coverage = matched_elements / len(key_elements) if key_elements else 0

        # Adjust score based on coverage
        quality_score = min(1.0, coverage * 1.2)  # Give some bonus for good coverage

        # Check for length (reasoning should be substantive)
        if len(actual_reasoning) < 20:
            quality_score *= 0.5

        return quality_score

    async def run_full_evaluation(self) -> EvaluationReport:
        """Run full evaluation pipeline on all test cases."""
        with logfire.span("full_evaluation_run"):
            results = []

            # Run all test cases
            for test_case in self.test_cases:
                result = await self.evaluate_single_test(test_case)
                results.append(result)
                self.historical_results.append(result)

            # Calculate metrics
            total_tests = len(results)
            passed = sum(1 for r in results if r.is_acceptable)
            failed = total_tests - passed
            accuracy = passed / total_tests if total_tests > 0 else 0

            # Calculate confidence metrics
            confidences = [r.confidence for r in results if r.confidence > 0]
            avg_confidence = statistics.mean(confidences) if confidences else 0

            # Calibration error: difference between confidence and actual accuracy
            calibration_error = abs(avg_confidence - accuracy)

            # Response time
            response_times = [r.response_time_ms for r in results]
            avg_response_time = statistics.mean(response_times) if response_times else 0

            # Results by category
            results_by_category = self._analyze_by_category(results)

            # Identify problem areas
            problem_areas = self._identify_problem_areas(results, results_by_category)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                accuracy, calibration_error, problem_areas
            )

            return EvaluationReport(
                timestamp=datetime.now(),
                total_tests=total_tests,
                passed=passed,
                failed=failed,
                accuracy=accuracy,
                average_confidence=avg_confidence,
                confidence_calibration_error=calibration_error,
                average_response_time_ms=avg_response_time,
                results_by_category=results_by_category,
                problem_areas=problem_areas,
                recommendations=recommendations,
            )

    def _analyze_by_category(
        self, results: list[EvaluationResult]
    ) -> dict[str, dict[str, float]]:
        """Analyze results by question category."""
        categories = {}

        for test_case, result in zip(self.test_cases, results, strict=False):
            for tag in test_case.tags:
                if tag not in categories:
                    categories[tag] = {
                        "total": 0,
                        "passed": 0,
                        "accuracy": 0,
                        "avg_confidence": 0,
                        "avg_response_time": 0,
                    }

                categories[tag]["total"] += 1
                if result.is_acceptable:
                    categories[tag]["passed"] += 1
                categories[tag]["avg_confidence"] += result.confidence
                categories[tag]["avg_response_time"] += result.response_time_ms

        # Calculate averages
        for tag in categories:
            total = categories[tag]["total"]
            if total > 0:
                categories[tag]["accuracy"] = categories[tag]["passed"] / total
                categories[tag]["avg_confidence"] /= total
                categories[tag]["avg_response_time"] /= total

        return categories

    def _identify_problem_areas(
        self, results: list[EvaluationResult], categories: dict[str, dict[str, float]]
    ) -> list[str]:
        """Identify areas needing improvement."""
        problems = []

        # Check category performance
        for category, metrics in categories.items():
            if metrics["accuracy"] < 0.8:
                problems.append(
                    f"Low accuracy in {category}: {metrics['accuracy']:.2%}"
                )

        # Check confidence calibration
        overconfident = [
            r for r in results if not r.is_acceptable and r.confidence > 0.7
        ]
        if len(overconfident) > len(results) * 0.1:
            problems.append(
                f"Model is overconfident on {len(overconfident)} incorrect answers"
            )

        # Check response times
        slow_responses = [r for r in results if r.response_time_ms > 5000]
        if slow_responses:
            problems.append(f"{len(slow_responses)} responses took over 5 seconds")

        return problems

    def _generate_recommendations(
        self, accuracy: float, calibration_error: float, problem_areas: list[str]
    ) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if accuracy < 0.9:
            recommendations.append(
                "Consider adding more few-shot examples for better accuracy"
            )

        if calibration_error > 0.15:
            recommendations.append(
                "Confidence scores need calibration - consider adjusting the critic model"
            )

        if any("bmi" in p.lower() for p in problem_areas):
            recommendations.append(
                "Add specific training examples for BMI calculations and interpretations"
            )

        if any("boolean" in p.lower() for p in problem_areas):
            recommendations.append(
                "Improve boolean question handling with clearer decision criteria"
            )

        if len(problem_areas) > 3:
            recommendations.append(
                "Consider fine-tuning the model on medical prior authorization data"
            )

        return recommendations

    async def continuous_improvement_cycle(self):
        """Run continuous evaluation and improvement."""
        while True:
            # Run evaluation
            report = await self.run_full_evaluation()

            # Log results
            logfire.info(
                "Evaluation completed",
                accuracy=report.accuracy,
                avg_confidence=report.average_confidence,
                problem_areas=report.problem_areas,
            )

            # Apply improvements if needed
            if report.accuracy < 0.95:
                await self._apply_improvements(report)

            # Wait before next cycle
            await asyncio.sleep(3600)  # Run hourly

    async def _apply_improvements(self, report: EvaluationReport):
        """Apply improvements based on evaluation results."""
        # This would implement automatic improvements like:
        # - Adjusting temperature settings
        # - Updating few-shot examples
        # - Modifying prompts
        # - Retraining critic model thresholds

        logfire.info(
            "Applying improvements based on evaluation",
            recommendations=report.recommendations,
        )
