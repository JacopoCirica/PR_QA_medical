#!/usr/bin/env python
"""
Demo script to show the AI-powered prior authorization system functionality.
This demonstrates the core features without requiring the full application to run.
"""

import json
from datetime import datetime
from typing import List, Dict, Any

# Sample patient data
sample_patient = {
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1975-05-15",
    "gender": "Male",
    "prescription": {
        "medication": "Zepbound",
        "dosage": "10 mg",
        "frequency": "once weekly",
        "duration": "ongoing"
    },
    "visit_notes": [
        "Patient presents for weight management consultation.",
        "Current weight: 245 lbs, Height: 5'10\" (70 inches)",
        "Calculated BMI: 35.2 kg/m²",
        "Has been following structured diet and exercise program for 9 months",
        "Previous medications tried: Metformin, Orlistat - insufficient response",
        "Comorbidities: Type 2 Diabetes (A1C: 8.2%), Hypertension (BP: 145/92)",
        "Patient has lost 15 lbs (6.1% of baseline weight) in past 3 months on current regimen"
    ]
}

# Sample questions from the prior authorization form
sample_questions = [
    {
        "type": "text",
        "key": "age",
        "content": "What is the patient's age in years?"
    },
    {
        "type": "text",
        "key": "bmi",
        "content": "What is the patient's body mass index (BMI) in kilograms per square meter (kg/m2)?"
    },
    {
        "type": "boolean",
        "key": "antiobesity_wt_mgmt_6m",
        "content": "Has the patient participated in a comprehensive weight-management program for at least 6 months?"
    },
    {
        "type": "boolean",
        "key": "antiobesity_bmi_ge30",
        "content": "Does the patient have a BMI greater than or equal to 30 kg per square meter?"
    },
    {
        "type": "boolean",
        "key": "antiobesity_bmi_ge27_comorbid",
        "content": "Does the patient have a BMI ≥ 27 kg/m² AND at least one weight-related comorbid condition?"
    },
    {
        "type": "text",
        "key": "diagnosis",
        "content": "What is the diagnosis for the medication being requested?"
    },
    {
        "type": "boolean",
        "key": "cont_wl_gt5percent",
        "content": "Has the patient had a weight loss of more than or equal to 5% of baseline body weight?"
    }
]

def calculate_age(date_of_birth: str) -> int:
    """Calculate age from date of birth."""
    dob = datetime.strptime(date_of_birth, "%Y-%m-%d")
    today = datetime.now()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

def simulate_llm_answer(patient: Dict, question: Dict) -> Dict[str, Any]:
    """
    Simulate LLM answer generation with reasoning.
    In the actual implementation, this would call OpenAI/Claude/Gemini API.
    """
    
    # Extract key information from patient data
    age = calculate_age(patient["date_of_birth"])
    visit_notes = " ".join(patient["visit_notes"])
    
    # Generate answers based on question key
    if question["key"] == "age":
        return {
            "value": f"{age}",
            "confidence": 1.0,
            "reasoning": f"Age calculated from date of birth ({patient['date_of_birth']}). Patient is {age} years old."
        }
    
    elif question["key"] == "bmi":
        return {
            "value": "35.2",
            "confidence": 0.95,
            "reasoning": "BMI value extracted from visit notes: 'Calculated BMI: 35.2 kg/m²'"
        }
    
    elif question["key"] == "antiobesity_wt_mgmt_6m":
        return {
            "value": True,
            "confidence": 0.92,
            "reasoning": "Visit notes indicate: 'Has been following structured diet and exercise program for 9 months', which exceeds the 6-month requirement."
        }
    
    elif question["key"] == "antiobesity_bmi_ge30":
        return {
            "value": True,
            "confidence": 0.98,
            "reasoning": "Patient's BMI is 35.2 kg/m², which is greater than the threshold of 30 kg/m²."
        }
    
    elif question["key"] == "antiobesity_bmi_ge27_comorbid":
        return {
            "value": True,
            "confidence": 0.96,
            "reasoning": "Patient has BMI of 35.2 (>27) and multiple comorbidities: Type 2 Diabetes and Hypertension as documented in visit notes."
        }
    
    elif question["key"] == "diagnosis":
        return {
            "value": "Obesity with comorbidities (Type 2 Diabetes, Hypertension)",
            "confidence": 0.89,
            "reasoning": "Based on BMI of 35.2 and documented comorbid conditions in patient records."
        }
    
    elif question["key"] == "cont_wl_gt5percent":
        return {
            "value": True,
            "confidence": 0.91,
            "reasoning": "Patient has lost 15 lbs representing 6.1% of baseline weight as stated in visit notes, exceeding the 5% threshold."
        }
    
    else:
        return {
            "value": "Unable to determine",
            "confidence": 0.0,
            "reasoning": "Question not recognized in the system."
        }

def simulate_critic_evaluation(answer: Dict) -> Dict[str, Any]:
    """
    Simulate the critic model evaluation.
    In actual implementation, this would be another LLM call.
    """
    
    # Simulate critic feedback based on confidence
    if answer["confidence"] >= 0.9:
        improvements = []
        evaluation = "High quality answer with strong evidence support"
    elif answer["confidence"] >= 0.8:
        improvements = ["Consider adding more specific citations from records"]
        evaluation = "Good answer but could benefit from more detail"
    else:
        improvements = [
            "Verify data extraction accuracy",
            "Add more context from patient records",
            "Cross-reference with other notes"
        ]
        evaluation = "Answer needs improvement for clinical use"
    
    return {
        "confidence_score": answer["confidence"],
        "improvements": improvements,
        "evaluation": evaluation,
        "is_acceptable": answer["confidence"] >= 0.8
    }

def main():
    """Run the demo."""
    print("🏥 AI-Powered Prior Authorization System - Demo")
    print("=" * 60)
    print("\n📋 Patient Information:")
    print(f"Name: {sample_patient['first_name']} {sample_patient['last_name']}")
    print(f"DOB: {sample_patient['date_of_birth']}")
    print(f"Medication: {sample_patient['prescription']['medication']} {sample_patient['prescription']['dosage']}")
    
    print("\n📝 Processing Prior Authorization Questions...")
    print("-" * 60)
    
    results = []
    
    for i, question in enumerate(sample_questions, 1):
        print(f"\n❓ Question {i}: {question['content']}")
        print(f"   Type: {question['type']}")
        
        # Simulate actor generating answer
        answer = simulate_llm_answer(sample_patient, question)
        
        # Simulate critic evaluation
        critic_eval = simulate_critic_evaluation(answer)
        
        # Display results
        print(f"\n   ✅ Answer: {answer['value']}")
        print(f"   📊 Confidence: {answer['confidence']:.1%}")
        print(f"   💭 Reasoning: {answer['reasoning']}")
        
        if critic_eval["improvements"]:
            print(f"   🔍 Critic Feedback: {critic_eval['evaluation']}")
            for improvement in critic_eval["improvements"]:
                print(f"      • {improvement}")
        
        results.append({
            "question": question["content"],
            "answer": answer["value"],
            "confidence": answer["confidence"],
            "acceptable": critic_eval["is_acceptable"]
        })
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("📊 Summary Statistics:")
    print("-" * 60)
    
    total_questions = len(results)
    acceptable_answers = sum(1 for r in results if r["acceptable"])
    avg_confidence = sum(r["confidence"] for r in results) / total_questions
    
    print(f"Total Questions: {total_questions}")
    print(f"Acceptable Answers: {acceptable_answers}/{total_questions} ({acceptable_answers/total_questions:.1%})")
    print(f"Average Confidence: {avg_confidence:.1%}")
    
    print("\n🎯 Key Features Demonstrated:")
    print("• Actor-Critic System for answer refinement")
    print("• Confidence scoring for each answer")
    print("• Detailed reasoning for transparency")
    print("• Medical context extraction from patient notes")
    print("• Conditional question handling")
    
    print("\n🌟 Advanced Capabilities (in full implementation):")
    print("• Real-time streaming of answers")
    print("• Clinical annotation UI for review")
    print("• Comprehensive evaluation pipeline")
    print("• Few-shot learning for improved accuracy")
    print("• Multi-model support (OpenAI, Anthropic, Google)")
    
    print("\n✨ This demo simulates the core logic without requiring API keys.")
    print("   The full implementation uses actual LLM APIs for production use.")
    
    # Save results to file
    output = {
        "timestamp": datetime.now().isoformat(),
        "patient": f"{sample_patient['first_name']} {sample_patient['last_name']}",
        "results": results,
        "statistics": {
            "total_questions": total_questions,
            "acceptable_answers": acceptable_answers,
            "average_confidence": avg_confidence
        }
    }
    
    with open("demo_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\n💾 Results saved to demo_results.json")

if __name__ == "__main__":
    main()
