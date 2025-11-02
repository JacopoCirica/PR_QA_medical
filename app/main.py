import asyncio
import json
from datetime import datetime

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse

from app.env import setup_env

from .annotation_ui import get_annotation_ui_html
from .evaluation import EvaluationPipeline
from .llm_service import LLMService
from .models import Answer, AnswerInput, AnswerOutput

# Make logfire optional
try:
    import logfire

    LOGFIRE_AVAILABLE = True
except ImportError:
    LOGFIRE_AVAILABLE = False

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

        def error(self, *args, **kwargs):
            pass

    logfire = DummyLogfire()

setup_env()

# Initialize services (updated)
llm_service = LLMService()
eval_pipeline = EvaluationPipeline(llm_service)

# Initialize the FastAPI application
app = FastAPI(
    title="Pharmacy Prior Authorization API",
    description="Advanced API for generating AI-powered answers to prior authorization questions with confidence scoring, actor-critic refinement, and continuous evaluation",
    version="2.0.0",
)

# In-memory storage for annotations and answers (in production, use a database)
annotations_db: dict[str, dict] = {}
answers_db: dict[str, dict] = {}  # Store generated answers for review


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Pharmacy Prior Authorization API is running",
        "status": "healthy",
        "features": {
            "confidence_scores": llm_service.enable_confidence,
            "actor_critic": llm_service.enable_actor_critic,
            "few_shot": llm_service.enable_few_shot,
            "reasoning_models": llm_service.enable_reasoning,
        },
    }


@app.post("/answers")
async def get_answers(data: AnswerInput) -> AnswerOutput:
    """
    Generate answers to prior authorization questions based on patient data.

    This endpoint uses advanced LLM techniques including:
    - Few-shot learning for improved accuracy
    - Actor-critic system for answer refinement
    - Confidence scoring for each answer
    - Conditional question handling
    """
    try:
        with logfire.span("process_authorization_request"):
            # Process all questions with the LLM service
            answers_with_confidence = await llm_service.process_questions_batch(
                data.patient, data.question_set.questions
            )

            # Convert to standard Answer format
            answers = [
                Answer(question=awc.question, value=awc.value)
                for awc in answers_with_confidence
            ]

            # Store answers for annotation UI (use timestamp as simple ID)
            from datetime import datetime

            auth_id = f"AUTH-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            for awc in answers_with_confidence:
                answer_key = f"{auth_id}:{awc.question.key}"
                answers_db[answer_key] = {
                    "authorization_id": auth_id,
                    "question": awc.question.dict(),
                    "value": awc.value,
                    "confidence": awc.confidence,
                    "reasoning": awc.reasoning,
                    "patient_name": f"{data.patient.first_name} {data.patient.last_name}",
                    "timestamp": datetime.now().isoformat(),
                    # Store complete patient information for UI display
                    "patient_data": {
                        "first_name": data.patient.first_name,
                        "last_name": data.patient.last_name,
                        "date_of_birth": data.patient.date_of_birth,
                        "gender": data.patient.gender,
                        "medication": data.patient.prescription.medication,
                        "dosage": data.patient.prescription.dosage,
                        "frequency": data.patient.prescription.frequency,
                        "duration": data.patient.prescription.duration,
                        "visit_notes": data.patient.visit_notes,
                    },
                }

            # Log metrics
            avg_confidence = (
                sum(awc.confidence for awc in answers_with_confidence)
                / len(answers_with_confidence)
                if answers_with_confidence
                else 0
            )
            logfire.info(
                "Answers generated",
                patient_id=f"{data.patient.first_name}_{data.patient.last_name}",
                num_questions=len(data.question_set.questions),
                num_answers=len(answers),
                avg_confidence=avg_confidence,
            )

            # Include authorization ID in response for UI reference
            print(f"\n✅ Answers generated and stored with Authorization ID: {auth_id}")
            print("   Use this ID in the Annotation UI to review these answers\n")
            return AnswerOutput(answers=answers)

    except Exception as e:
        logfire.error("Error generating answers", error=str(e))
        raise HTTPException(
            status_code=500, detail=f"Error generating answers: {str(e)}"
        )


@app.post("/answers/with-confidence")
async def get_answers_with_confidence(data: AnswerInput) -> dict:
    """
    Generate answers with confidence scores and reasoning.

    Returns detailed information including:
    - Answer values
    - Confidence scores (0.0 to 1.0)
    - Reasoning for each answer
    - Suggested improvements from critic model
    """
    try:
        with logfire.span("process_authorization_with_confidence"):
            answers_with_confidence = await llm_service.process_questions_batch(
                data.patient, data.question_set.questions
            )

            return {
                "answers": [
                    {
                        "question_key": awc.question.key,
                        "question_content": awc.question.content,
                        "value": awc.value,
                        "confidence": awc.confidence,
                        "reasoning": awc.reasoning,
                        "improvements": awc.improvements,
                    }
                    for awc in answers_with_confidence
                ],
                "metadata": {
                    "patient_name": f"{data.patient.first_name} {data.patient.last_name}",
                    "medication": data.patient.prescription.medication,
                    "timestamp": datetime.now().isoformat(),
                    "model_features": {
                        "confidence_scoring": llm_service.enable_confidence,
                        "actor_critic": llm_service.enable_actor_critic,
                        "few_shot_learning": llm_service.enable_few_shot,
                    },
                },
            }

    except Exception as e:
        logfire.error("Error generating answers with confidence", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


async def generate_answers_stream(patient, questions):
    """Generator function for streaming answers."""
    for question in questions:
        answer = await llm_service.generate_answer_with_confidence(patient, question)

        # Yield the answer as JSON with newline delimiter
        yield (
            json.dumps(
                {
                    "question_key": question.key,
                    "question_content": question.content,
                    "value": answer.value,
                    "confidence": answer.confidence,
                    "reasoning": answer.reasoning,
                }
            )
            + "\n"
        )

        # Small delay to simulate processing
        await asyncio.sleep(0.1)


@app.post("/answers/stream")
async def get_answers_stream(data: AnswerInput):
    """
    Stream answers as they are generated for better UX.

    Returns a stream of JSON objects, one per line, as answers are generated.
    This provides immediate feedback to users instead of waiting for all answers.
    """
    return StreamingResponse(
        generate_answers_stream(data.patient, data.question_set.questions),
        media_type="application/x-ndjson",
    )


# Evaluation endpoints
@app.post("/evaluation/run")
async def run_evaluation(background_tasks: BackgroundTasks) -> dict:
    """
    Run a full evaluation cycle on the test suite.

    This endpoint triggers a comprehensive evaluation of the model's performance
    using predefined test cases.
    """
    try:
        report = await eval_pipeline.run_full_evaluation()

        return {
            "status": "completed",
            "report": {
                "timestamp": report.timestamp.isoformat(),
                "total_tests": report.total_tests,
                "passed": report.passed,
                "failed": report.failed,
                "accuracy": report.accuracy,
                "average_confidence": report.average_confidence,
                "confidence_calibration_error": report.confidence_calibration_error,
                "average_response_time_ms": report.average_response_time_ms,
                "results_by_category": report.results_by_category,
                "problem_areas": report.problem_areas,
                "recommendations": report.recommendations,
            },
        }
    except Exception as e:
        logfire.error("Evaluation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evaluation/history")
async def get_evaluation_history(limit: int = 10) -> dict:
    """
    Get historical evaluation results.

    Returns the most recent evaluation results for tracking performance over time.
    """
    recent_results = (
        eval_pipeline.historical_results[-limit:]
        if eval_pipeline.historical_results
        else []
    )

    return {
        "total_evaluations": len(eval_pipeline.historical_results),
        "recent_results": [
            {
                "test_case_id": r.test_case_id,
                "question_key": r.question_key,
                "is_correct": r.is_correct,
                "confidence": r.confidence,
                "response_time_ms": r.response_time_ms,
            }
            for r in recent_results
        ],
    }


# Annotation endpoints for clinical review
@app.get("/answers/get/{authorization_id}/{question_key}")
async def get_answer_for_review(authorization_id: str, question_key: str):
    """
    Retrieve a previously generated answer for annotation/review.
    This endpoint is used by the annotation UI to load real answers.
    """
    answer_key = f"{authorization_id}:{question_key}"

    if answer_key in answers_db:
        return answers_db[answer_key]
    else:
        # Return a placeholder if no real answer exists yet
        return {
            "error": "Answer not found",
            "message": f"No answer found for {authorization_id}:{question_key}",
            "suggestion": "Generate answers first using /answers endpoint",
        }


@app.get("/answers/list")
async def list_available_answers():
    """
    List all available answers that can be reviewed.
    """
    return {
        "total": len(answers_db),
        "answers": list(answers_db.values())[:20],  # Return last 20 for UI
    }


@app.post("/annotations/submit")
async def submit_annotation(
    authorization_id: str,
    question_key: str,
    original_answer: str | bool,
    corrected_answer: str | bool,
    feedback: str,
    reviewer_id: str,
) -> dict:
    """
    Submit clinical staff annotation for an answer.

    This endpoint allows clinical reviewers to provide feedback on generated answers,
    which can be used to improve the model.
    """
    annotation_id = f"{authorization_id}_{question_key}_{datetime.now().timestamp()}"

    annotations_db[annotation_id] = {
        "authorization_id": authorization_id,
        "question_key": question_key,
        "original_answer": original_answer,
        "corrected_answer": corrected_answer,
        "feedback": feedback,
        "reviewer_id": reviewer_id,
        "timestamp": datetime.now().isoformat(),
    }

    logfire.info(
        "Annotation submitted",
        annotation_id=annotation_id,
        question_key=question_key,
        reviewer_id=reviewer_id,
    )

    return {
        "status": "success",
        "annotation_id": annotation_id,
        "message": "Annotation saved successfully",
    }


@app.get("/annotations/list")
async def list_annotations(
    authorization_id: str | None = None, reviewer_id: str | None = None, limit: int = 50
) -> dict:
    """
    List submitted annotations with optional filtering.
    """
    filtered_annotations = []

    for ann_id, annotation in annotations_db.items():
        if authorization_id and annotation["authorization_id"] != authorization_id:
            continue
        if reviewer_id and annotation["reviewer_id"] != reviewer_id:
            continue

        filtered_annotations.append({"id": ann_id, **annotation})

    # Sort by timestamp and limit
    filtered_annotations.sort(key=lambda x: x["timestamp"], reverse=True)
    filtered_annotations = filtered_annotations[:limit]

    return {"total": len(filtered_annotations), "annotations": filtered_annotations}


@app.get("/metrics")
async def get_metrics() -> dict:
    """
    Get current system metrics and performance indicators.
    """
    # Calculate metrics from historical data
    if eval_pipeline.historical_results:
        recent_results = eval_pipeline.historical_results[-100:]  # Last 100 results
        accuracy = sum(1 for r in recent_results if r.is_correct) / len(recent_results)
        avg_confidence = sum(r.confidence for r in recent_results) / len(recent_results)
        avg_response_time = sum(r.response_time_ms for r in recent_results) / len(
            recent_results
        )
    else:
        accuracy = avg_confidence = avg_response_time = 0

    return {
        "performance": {
            "accuracy": accuracy,
            "average_confidence": avg_confidence,
            "average_response_time_ms": avg_response_time,
        },
        "annotations": {
            "total_submitted": len(annotations_db),
            "unique_reviewers": len(
                set(a["reviewer_id"] for a in annotations_db.values())
            )
            if annotations_db
            else 0,
        },
        "model_configuration": {
            "confidence_scoring_enabled": llm_service.enable_confidence,
            "actor_critic_enabled": llm_service.enable_actor_critic,
            "few_shot_enabled": llm_service.enable_few_shot,
            "reasoning_models_enabled": llm_service.enable_reasoning,
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/annotation-ui", response_class=HTMLResponse)
async def annotation_ui():
    """
    Serve the annotation UI for clinical staff review.

    This provides a web interface for clinical staff to:
    - Review AI-generated answers
    - Submit corrections and feedback
    - View annotation history
    - Monitor system performance
    """
    return get_annotation_ui_html()
