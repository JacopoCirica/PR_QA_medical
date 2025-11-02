#!/usr/bin/env python
"""Test script to verify OpenAI API key is working."""

import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

async def test_openai():
    """Test if OpenAI API key is configured and working."""
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "sk-your-actual-api-key-here":
        print("❌ OpenAI API key not configured!")
        print("   Please add your actual API key to .env file")
        return False
    
    try:
        # Initialize client
        client = AsyncOpenAI(api_key=api_key)
        
        # Test with a simple request
        print("🔄 Testing OpenAI API connection...")
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API is working!'"}],
            max_tokens=10
        )
        
        print("✅ OpenAI API is working!")
        print(f"   Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to OpenAI: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_openai())
