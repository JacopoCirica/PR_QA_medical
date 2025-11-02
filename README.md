# AI-Powered Prior Authorization System

> **Take-Home Assessment Implementation** - AI Engineer Role

This repository contains a comprehensive implementation of an AI-powered prior authorization system for pharmacy requests, featuring actor-critic answer generation, confidence scoring, and a clinical annotation UI.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -e .

# Set API key (optional - works in demo mode without it)
export OPENAI_API_KEY="your-key-here"

# Run the server
uvicorn app.main:app --reload

# Access the application
# - API: http://localhost:8000
# - Annotation UI: http://localhost:8000/annotation-ui
# - API Docs: http://localhost:8000/docs
```

## ✨ Key Features

- **🤖 Actor-Critic AI System**: Two-stage answer generation with critic evaluation
- **📊 Confidence Scoring**: Every answer includes 0.0-1.0 confidence score
- **🎯 Few-Shot Learning**: Medical examples guide the model
- **🔬 Evaluation Pipeline**: Automated testing and metrics tracking
- **💻 Clinical Annotation UI**: Web interface for human review with patient summaries
- **⚡ Real-time Streaming**: Answers generated and delivered in real-time
- **📝 GPT-4.1 Optimized**: Prompts following OpenAI best practices

## 📚 Documentation

- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Complete technical documentation

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test with example request
curl -X POST http://localhost:8000/answers \
  -H "Content-Type: application/json" \
  -d @sample_data/example_request_isaiah.json

# Run evaluation pipeline
curl -X POST http://localhost:8000/evaluation/run
```

## 📂 Project Structure

```
├── app/
│   ├── main.py           # FastAPI application with all endpoints
│   ├── llm_service.py    # AI logic (actor-critic, few-shot, confidence)
│   ├── models.py         # Pydantic data models
│   ├── evaluation.py     # Testing and metrics pipeline
│   ├── annotation_ui.py  # Clinical review web interface
│   └── env.py            # Environment configuration
├── sample_data/          # Example request files and test data
├── tests/                # Test suite
└── docs/                 # Assessment requirements

```

## 🎯 Assessment Requirements

**Original Requirements**: [AI Product Engineer Instructions](/docs/ai_product_engineer.md)

**All requirements completed** ✅




