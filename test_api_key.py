#!/usr/bin/env python3

import os
import sys
sys.path.append('src')

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from src.ai.openrouter_client import OpenRouterClient

def test_api_key():
    print("Testing API key...")

    # Load API key from environment
    api_key = os.getenv('OPENROUTER_API_KEY')
    print(f"API Key present: {api_key is not None}")
    if api_key:
        print(f"API Key length: {len(api_key)}")
        # Don't print the full key for security

    try:
        client = OpenRouterClient()
        print("Client created successfully")

        # Test connection
        print("Testing connection...")
        test_prompt = "Hello, this is a test message."
        test_system_prompt = "You are a helpful assistant. Respond briefly."

        response = client.call_llm(
            prompt=test_prompt,
            system_prompt=test_system_prompt,
            temperature=0.5
        )

        text_response = client.extract_text_response(response)
        print(f"Connection test successful. Response: {text_response}")
        return True

    except Exception as e:
        print(f"Connection test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_key()
