"""
LLM Service module for handling AI-powered answer generation.
Implements advanced prompting strategies including few-shot learning,
actor-critic systems, and reasoning models.
"""

import json
import os
from datetime import datetime
from enum import Enum
from typing import Any

from openai import AsyncOpenAI
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

    logfire = DummyLogfire()

from .models import Patient, Question


class ModelType(Enum):
    """Available model types for different use cases."""

    STANDARD = "gpt-4-turbo-preview"
    REASONING = "o1-preview"
    CRITIC = "gpt-4-turbo-preview"
    FAST = "gpt-3.5-turbo"


class AnswerWithConfidence(BaseModel):
    """Answer with confidence score and reasoning."""

    question: Question
    value: str | bool
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str | None = None
    improvements: list[str] | None = None


class FewShotExample(BaseModel):
    """Few-shot example for prompt engineering."""

    patient_context: str
    question: str
    answer: str | bool
    reasoning: str


class LLMService:
    """Advanced LLM service with multiple prompting strategies."""

    def __init__(self):
        # Make OpenAI client optional - only initialize if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            try:
                self.client = AsyncOpenAI(api_key=api_key)
            except Exception as e:
                print(f"⚠️  Could not initialize OpenAI client: {e}")
                self.client = None
        else:
            print("ℹ️  OpenAI API key not configured. LLM features will be simulated.")
            self.client = None

        self.enable_confidence = (
            os.getenv("ENABLE_CONFIDENCE_SCORES", "true").lower() == "true"
        )
        self.enable_actor_critic = (
            os.getenv("ENABLE_ACTOR_CRITIC", "true").lower() == "true"
        )
        self.enable_few_shot = os.getenv("ENABLE_FEW_SHOT", "true").lower() == "true"
        self.enable_reasoning = (
            os.getenv("ENABLE_REASONING_MODELS", "false").lower() == "true"
        )

        # Initialize few-shot examples
        self.few_shot_examples = self._load_few_shot_examples()

    def _load_few_shot_examples(self) -> list[FewShotExample]:
        """Load few-shot examples for better prompt engineering."""
        return [
            FewShotExample(
                patient_context="Patient: 45-year-old male, BMI 32.5, diagnosed with Type 2 diabetes and hypertension",
                question="Does the patient have a BMI greater than or equal to 30 kg per square meter?",
                answer=True,
                reasoning="The patient's BMI is 32.5 kg/m², which is greater than 30 kg/m².",
            ),
            FewShotExample(
                patient_context="Patient: 35-year-old female, weight 180 lbs, height 5'4\", participated in diet program for 8 months",
                question="Has the patient participated in a comprehensive weight-management program for at least 6 months?",
                answer=True,
                reasoning="The patient has participated in a diet program for 8 months, which exceeds the 6-month requirement.",
            ),
            FewShotExample(
                patient_context="Patient on Zepbound 10mg weekly for 4 months, lost 12% of baseline weight",
                question="Has the patient had a weight loss of more than or equal to 5% of baseline body weight?",
                answer=True,
                reasoning="The patient has lost 12% of baseline weight, which is significantly more than the required 5%.",
            ),
        ]

    def _calculate_age(self, date_of_birth: str) -> int:
        """Calculate patient age from date of birth."""
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d")
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age

    def _extract_patient_context(self, patient: Patient) -> str:
        """Extract comprehensive context from patient data."""
        age = self._calculate_age(patient.date_of_birth)

        context_parts = [
            "Patient Information:",
            f"- Name: {patient.first_name} {patient.last_name}",
            f"- Age: {age} years",
            f"- Gender: {patient.gender}",
            f"- Date of Birth: {patient.date_of_birth}",
            "\nCurrent Prescription:",
            f"- Medication: {patient.prescription.medication}",
            f"- Dosage: {patient.prescription.dosage}",
            f"- Frequency: {patient.prescription.frequency}",
            f"- Duration: {patient.prescription.duration}",
            "\nVisit Notes:",
        ]

        for i, note in enumerate(patient.visit_notes, 1):
            context_parts.append(f"{i}. {note}")

        return "\n".join(context_parts)

    def _build_few_shot_prompt(self, examples: list[FewShotExample]) -> str:
        """Build few-shot learning prompt section."""
        if not self.enable_few_shot or not examples:
            return ""

        prompt_parts = ["\n### Examples of Correct Answers:\n"]

        for i, example in enumerate(examples[:3], 1):  # Use top 3 examples
            prompt_parts.append(f"\nExample {i}:")
            prompt_parts.append(f"Context: {example.patient_context}")
            prompt_parts.append(f"Question: {example.question}")
            prompt_parts.append(f"Answer: {example.answer}")
            prompt_parts.append(f"Reasoning: {example.reasoning}")

        prompt_parts.append("\n---\n")
        return "\n".join(prompt_parts)

    async def _generate_base_answer(
        self,
        patient_context: str,
        question: Question,
        model: ModelType = ModelType.STANDARD,
    ) -> tuple[Any, str]:
        """Generate base answer using specified model."""

        # If no client available, return simulated answer
        if not self.client:
            return self._simulate_answer(patient_context, question)

        few_shot_prompt = self._build_few_shot_prompt(self.few_shot_examples)

        system_prompt = """You are a medical prior authorization specialist AI assistant.

Your task is to answer prior authorization questions with ABSOLUTE PRECISION based ONLY on the provided patient information.

═══════════════════════════════════════════════════════════════
CRITICAL INSTRUCTIONS - FOLLOW THESE LITERALLY:
═══════════════════════════════════════════════════════════════

1. BASE ANSWERS STRICTLY ON PROVIDED DATA
   - Extract information ONLY from the patient context provided
   - Do NOT infer, assume, or extrapolate beyond what is explicitly stated
   - If data is missing, you MUST state: "Information not available in patient records"

2. QUESTION TYPE REQUIREMENTS
   - Boolean questions: Return ONLY true or false (lowercase)
   - Text questions: Return concise, factual answers as strings
   - ALWAYS include units for measurements (kg/m², years, lbs, etc.)

3. MEDICAL ACCURACY REQUIREMENTS
   - Use precise medical terminology
   - Verify calculations (e.g., BMI from height/weight if provided)
   - Consider ALL visit notes and medical history sections
   - Maintain consistency with clinical standards

4. STEP-BY-STEP REASONING (REQUIRED)
   - First, identify the relevant data in patient context
   - Second, extract or calculate the required value
   - Third, verify the answer meets the question requirements
   - Fourth, formulate your reasoning explaining your answer

5. RESPONSE FORMAT (STRICT JSON)
   - You MUST return valid JSON with these exact keys
   - "answer": <your answer value - boolean for boolean questions, string for text questions>
   - "reasoning": <your step-by-step reasoning as a string>
   - "supporting_data": <specific patient data points you used as a string>

═══════════════════════════════════════════════════════════════

EXAMPLE GOOD RESPONSES:

For boolean question "Does patient have BMI ≥30?":
{
  "answer": true,
  "reasoning": "Patient's BMI is explicitly stated as 37.4 kg/m² in vital signs, which exceeds 30 kg/m²",
  "supporting_data": "BMI: 37.4 kg/m² from visit notes dated 2025-08-15"
}

For text question "What is patient's age?":
{
  "answer": "55 years",
  "reasoning": "Calculated from DOB 1970-03-11 to current date, also explicitly stated in visit notes as 55 years old",
  "supporting_data": "DOB: 1970-03-11, Visit notes confirm age: 55 years"
}

Your answers will be reviewed by medical professionals. Accuracy is paramount."""

        user_prompt = f"""{few_shot_prompt}

═══════════════════════════════════════════════════════════════
PATIENT INFORMATION:
═══════════════════════════════════════════════════════════════
{patient_context}
═══════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════
QUESTION TO ANSWER:
═══════════════════════════════════════════════════════════════
Type: {question.type}
Key: {question.key}
Question: {question.content}
═══════════════════════════════════════════════════════════════

INSTRUCTIONS - COMPLETE THESE STEPS IN ORDER:

STEP 1: Search the patient context above for relevant information
   - Look in: demographics, vital signs, visit notes, medical history
   - Identify: the specific data points that answer this question

STEP 2: Extract or calculate the answer
   - For boolean: determine true or false based on evidence
   - For text: extract the exact value or state unavailability
   - Include units: "37.4 kg/m²" not "37.4"

STEP 3: Verify your answer
   - Check: Does it answer what was asked?
   - Check: Is it supported by the patient data?
   - Check: Is the format correct for the question type?

STEP 4: Formulate your response
   - Write clear reasoning citing specific patient data
   - Note which section of patient context you used

STEP 5: Return ONLY this exact JSON structure:
{{
    "answer": <your answer value>,
    "reasoning": "<your step-by-step reasoning>",
    "supporting_data": "<specific data from patient context>"
}}

REMINDER: 
- Boolean questions require boolean true/false (not strings)
- Text questions require strings
- Missing data = "Information not available in patient records"
- You MUST return valid JSON only"""

        with logfire.span("generate_base_answer", question_key=question.key):
            response = await self.client.chat.completions.create(
                model=model.value,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent medical answers
                response_format={"type": "json_object"},
            )

        result = json.loads(response.choices[0].message.content)

        # Ensure answer type matches question type
        answer = result["answer"]
        if question.type == "text":
            # Convert to string for text questions
            answer = str(answer)
        elif question.type == "boolean":
            # Convert to boolean for boolean questions
            if isinstance(answer, str):
                answer = answer.lower() in ("true", "yes", "1")
            else:
                answer = bool(answer)

        return answer, result["reasoning"]

    def _simulate_answer(
        self, patient_context: str, question: Question
    ) -> tuple[Any, str]:
        """Simulate an answer when no LLM client is available."""
        # Basic simulation logic for demo purposes
        if question.type == "boolean":
            # Check for common patterns in the context
            if "bmi" in question.key.lower():
                if "32" in patient_context or "35" in patient_context:
                    return True, "Patient BMI exceeds threshold based on available data"
            return False, "Unable to determine from available information"
        else:
            # Text questions
            if question.key == "age":
                return "45", "Age estimated from available patient data"
            elif question.key == "bmi":
                return "32.5", "BMI value extracted from patient records"
            return "Information not available", "Cannot determine from current data"

    async def _critic_evaluate_answer(
        self,
        patient_context: str,
        question: Question,
        proposed_answer: Any,
        reasoning: str,
    ) -> tuple[float, list[str]]:
        """Critic model evaluates the proposed answer."""

        if not self.enable_actor_critic or not self.client:
            return 0.9, []  # Default high confidence if critic is disabled or no client

        critic_prompt = f"""You are a medical expert critic evaluating prior authorization answers for accuracy and completeness.

═══════════════════════════════════════════════════════════════
YOUR TASK: Evaluate the proposed answer using strict medical standards
═══════════════════════════════════════════════════════════════

### PATIENT CONTEXT:
───────────────────────────────────────────────────────────────
{patient_context}
───────────────────────────────────────────────────────────────

### QUESTION BEING ANSWERED:
───────────────────────────────────────────────────────────────
{question.content}
───────────────────────────────────────────────────────────────

### PROPOSED ANSWER TO EVALUATE:
───────────────────────────────────────────────────────────────
Answer: {proposed_answer}
Reasoning: {reasoning}
───────────────────────────────────────────────────────────────

═══════════════════════════════════════════════════════════════
EVALUATION CRITERIA - ASSESS EACH ONE EXPLICITLY:
═══════════════════════════════════════════════════════════════

1. MEDICAL ACCURACY
   - Is the answer medically correct based on the patient data?
   - Are calculations correct (if applicable)?
   - Is medical terminology used properly?

2. COMPLETENESS
   - Does the answer fully address what was asked?
   - Are all relevant aspects covered?
   - Is any critical information missing?

3. EVIDENCE SUPPORT
   - Is the answer directly supported by patient information?
   - Can you trace the answer to specific data points?
   - Are any unsupported assumptions made?

4. CLARITY & PRECISION
   - Is the answer unambiguous?
   - Are units included where needed?
   - Is the language appropriate for medical review?

5. PRIOR AUTH COMPLIANCE
   - Does it meet standard prior authorization requirements?
   - Is it suitable for insurance review?

═══════════════════════════════════════════════════════════════
INSTRUCTIONS - FOLLOW EXACTLY:
═══════════════════════════════════════════════════════════════

STEP 1: Evaluate each of the 5 criteria above
STEP 2: Assign a confidence score:
   - 1.0 = Perfect, no issues whatsoever
   - 0.9 = Excellent, minor presentation improvements possible
   - 0.8 = Good, minor accuracy or completeness gaps
   - 0.7 = Acceptable but needs improvement
   - 0.6 or below = Significant issues, requires refinement

STEP 3: If score < 0.8, list SPECIFIC, ACTIONABLE improvements
   - Be concrete: "Include BMI unit" not "improve clarity"
   - Reference the patient data: "Use weight from visit note 1"
   - Prioritize accuracy over style

STEP 4: Return ONLY valid JSON with these EXACT keys:
{{
    "confidence_score": <float between 0.0 and 1.0>,
    "improvements": [<array of strings, empty if none needed>],
    "evaluation_notes": "<your detailed evaluation as a string>",
    "is_acceptable": <boolean: true if score >= 0.7, false otherwise>
}}

You MUST return valid JSON. Do NOT include any text outside the JSON object."""

        with logfire.span("critic_evaluation", question_key=question.key):
            response = await self.client.chat.completions.create(
                model=ModelType.CRITIC.value,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical expert reviewer specializing in prior authorization accuracy.",
                    },
                    {"role": "user", "content": critic_prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )

        result = json.loads(response.choices[0].message.content)
        return result["confidence_score"], result.get("improvements", [])

    async def _refine_answer_with_feedback(
        self,
        patient_context: str,
        question: Question,
        original_answer: Any,
        improvements: list[str],
    ) -> tuple[Any, str]:
        """Refine answer based on critic feedback."""

        if not self.client:
            return (
                original_answer,
                "Answer maintained (no LLM client available for refinement)",
            )

        refinement_prompt = f"""You are refining a prior authorization answer based on expert medical reviewer feedback.

═══════════════════════════════════════════════════════════════
YOUR TASK: Create an improved answer that addresses ALL feedback
═══════════════════════════════════════════════════════════════

### PATIENT CONTEXT:
───────────────────────────────────────────────────────────────
{patient_context}
───────────────────────────────────────────────────────────────

### QUESTION:
───────────────────────────────────────────────────────────────
Type: {question.type}
Question: {question.content}
───────────────────────────────────────────────────────────────

### ORIGINAL ANSWER (needs improvement):
───────────────────────────────────────────────────────────────
{original_answer}
───────────────────────────────────────────────────────────────

### EXPERT FEEDBACK - ADDRESS EACH POINT:
───────────────────────────────────────────────────────────────
{chr(10).join(f"{i + 1}. {imp}" for i, imp in enumerate(improvements))}
───────────────────────────────────────────────────────────────

═══════════════════════════════════════════════════════════════
INSTRUCTIONS - FOLLOW STEP BY STEP:
═══════════════════════════════════════════════════════════════

STEP 1: Review each improvement point carefully
STEP 2: Re-examine the patient context for relevant data
STEP 3: Create a refined answer that:
   - Addresses ALL improvement points
   - Maintains any correct aspects of the original
   - Stays strictly within the patient data provided
   - Follows the question type (boolean → true/false, text → string)
STEP 4: Document what you changed and why

STEP 5: Return ONLY valid JSON with these EXACT keys:
{{
    "refined_answer": <your improved answer - boolean for boolean questions, string for text questions>,
    "reasoning": "<comprehensive reasoning for the refined answer>",
    "changes_made": [<array of strings describing specific changes>]
}}

CRITICAL: Ensure your refined_answer matches the question type exactly.
For boolean questions: use true or false (not "true" or "false" as strings)
For text questions: use strings with appropriate units

You MUST return valid JSON only. No additional text."""

        with logfire.span("refine_answer", question_key=question.key):
            response = await self.client.chat.completions.create(
                model=ModelType.STANDARD.value,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical AI specialist refining prior authorization answers based on expert feedback. Follow instructions precisely and return only valid JSON.",
                    },
                    {"role": "user", "content": refinement_prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )

        result = json.loads(response.choices[0].message.content)

        # Ensure answer type matches question type
        answer = result["refined_answer"]
        if question.type == "text":
            # Convert to string for text questions
            answer = str(answer)
        elif question.type == "boolean":
            # Convert to boolean for boolean questions
            if isinstance(answer, str):
                answer = answer.lower() in ("true", "yes", "1")
            else:
                answer = bool(answer)

        return answer, result["reasoning"]

    async def generate_answer_with_confidence(
        self,
        patient: Patient,
        question: Question,
        previous_answers: dict[str, Any] | None = None,
    ) -> AnswerWithConfidence:
        """Generate answer with confidence score using actor-critic approach."""

        patient_context = self._extract_patient_context(patient)

        # Add previous answers context if available
        if previous_answers:
            context_parts = [patient_context, "\n### Previously Answered Questions:"]
            for key, value in previous_answers.items():
                context_parts.append(f"- {key}: {value}")
            patient_context = "\n".join(context_parts)

        # Step 1: Generate initial answer (Actor)
        answer_value, reasoning = await self._generate_base_answer(
            patient_context, question
        )

        # Step 2: Evaluate answer (Critic)
        confidence, improvements = await self._critic_evaluate_answer(
            patient_context, question, answer_value, reasoning
        )

        # Step 3: Refine if confidence is low
        if confidence < 0.8 and improvements and self.enable_actor_critic:
            answer_value, reasoning = await self._refine_answer_with_feedback(
                patient_context, question, answer_value, improvements
            )
            # Re-evaluate after refinement
            confidence, _ = await self._critic_evaluate_answer(
                patient_context, question, answer_value, reasoning
            )

        return AnswerWithConfidence(
            question=question,
            value=answer_value,
            confidence=confidence if self.enable_confidence else 1.0,
            reasoning=reasoning,
            improvements=improvements if improvements else None,
        )

    async def process_questions_batch(
        self, patient: Patient, questions: list[Question]
    ) -> list[AnswerWithConfidence]:
        """Process multiple questions with dependency handling."""

        answers_with_confidence = []
        answered_questions = {}

        for question in questions:
            # Check if question should be visible based on conditions
            if question.visible_if and not self._evaluate_condition(
                question.visible_if, answered_questions
            ):
                continue

            # Generate answer with context of previous answers
            answer = await self.generate_answer_with_confidence(
                patient, question, answered_questions
            )

            answers_with_confidence.append(answer)
            answered_questions[question.key] = answer.value

        return answers_with_confidence

    def _evaluate_condition(self, condition: str, answers: dict[str, Any]) -> bool:
        """Evaluate visibility conditions for conditional questions."""
        if not condition:
            return True

        # Parse simple conditions like "{key} = value"
        # This is a simplified implementation - could be extended
        import re

        # Handle "and" conditions
        if " and " in condition:
            parts = condition.split(" and ")
            return all(
                self._evaluate_condition(part.strip(), answers) for part in parts
            )

        # Handle single conditions
        pattern = r"\{([^}]+)\}\s*=\s*(.+)"
        match = re.match(pattern, condition.strip())

        if match:
            key = match.group(1)
            expected_value = match.group(2).strip()

            if key not in answers:
                return False

            actual_value = str(answers[key]).lower()
            expected_value = expected_value.lower()

            return actual_value == expected_value

        return True
