#!/usr/bin/env python
"""
Quick setup and run script for the Prior Authorization API.
This script helps users get started quickly with the application.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10 or higher is required")
        print(f"   You have Python {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor} detected")


def check_uv_installed():
    """Check if uv is installed."""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✅ uv is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uv is not installed")
        print("   Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False


def setup_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file exists")
        # Check if OPENAI_API_KEY is set
        with open(env_file) as f:
            content = f.read()
            if "OPENAI_API_KEY=" not in content or "OPENAI_API_KEY=your" in content:
                print("⚠️  Warning: OPENAI_API_KEY not configured in .env")
                print("   Please add your OpenAI API key to .env file")
                return False
        return True
    else:
        print("📝 Creating .env file...")
        env_content = """# LLM API Keys (at least one required)
OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# GOOGLE_API_KEY=your_google_api_key_here

# Optional: Pydantic Logfire for observability
# LOGFIRE_KEY=your_logfire_key_here

# Model Configuration
DEFAULT_MODEL=gpt-4-turbo-preview
REASONING_MODEL=o1-preview
CRITIC_MODEL=gpt-4-turbo-preview

# Feature Flags
ENABLE_CONFIDENCE_SCORES=true
ENABLE_ACTOR_CRITIC=true
ENABLE_FEW_SHOT=true
ENABLE_REASONING_MODELS=false

# Server Configuration
PORT=8000
HOST=0.0.0.0
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        
        print("✅ .env file created")
        print("⚠️  Please edit .env and add your API keys before running the app")
        return False


def install_dependencies():
    """Install project dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run(["uv", "sync"], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def run_app():
    """Run the FastAPI application."""
    print("\n🚀 Starting the application...")
    print("=" * 50)
    print("📍 API Documentation: http://localhost:8000/docs")
    print("🔬 Annotation UI: http://localhost:8000/annotation-ui")
    print("📊 Metrics: http://localhost:8000/metrics")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        subprocess.run(["uv", "run", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")


def run_tests():
    """Run the test suite."""
    print("\n🧪 Running tests...")
    try:
        subprocess.run(["uv", "run", "pytest", "-v"], check=True)
        print("✅ All tests passed")
    except subprocess.CalledProcessError:
        print("❌ Some tests failed")


def main():
    """Main entry point."""
    print("🏥 Prior Authorization API Setup")
    print("=" * 50)
    
    # Check prerequisites
    check_python_version()
    
    if not check_uv_installed():
        print("\n❌ Please install uv first")
        sys.exit(1)
    
    # Setup environment
    env_ready = setup_env_file()
    
    if not env_ready:
        print("\n⚠️  Please configure your API keys in .env file")
        print("   Then run this script again")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Ask user what to do
    print("\nWhat would you like to do?")
    print("1. Run the application")
    print("2. Run tests")
    print("3. Both (tests then app)")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == "1":
        run_app()
    elif choice == "2":
        run_tests()
    elif choice == "3":
        run_tests()
        print("\n" + "=" * 50)
        run_app()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
