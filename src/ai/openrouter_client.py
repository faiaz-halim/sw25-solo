import os
import requests
import json
import time
from typing import Dict, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Client for interacting with the OpenRouter API."""

    def __init__(self, api_key: str = None):
        """
        Initialize the OpenRouter client.

        Args:
            api_key (str): OpenRouter API key. If not provided, will be loaded from environment variables.
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable or pass it directly.")

        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/faiaz/SwordWorld2.5",  # Optional, for OpenRouter analytics
        }

    def call_llm(self, prompt: str, system_prompt: str = None, model: str = "qwen/qwen3-coder:free",
                 max_tokens: int = 1000, temperature: float = 0.7, retries: int = 3) -> Dict:
        """
        Call the LLM through OpenRouter API.

        Args:
            prompt (str): The user prompt to send to the LLM
            system_prompt (str): System prompt to guide the LLM's behavior
            model (str): The model to use (default: gpt-3.5-turbo)
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Temperature for response randomness (0.0 to 1.0)
            retries (int): Number of retry attempts for failed requests

        Returns:
            Dict: Response from the LLM containing the generated text and metadata

        Raises:
            Exception: If the API call fails after all retries
        """
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add user prompt
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        url = f"{self.base_url}/chat/completions"

        for attempt in range(retries + 1):
            try:
                response = requests.post(url, headers=self.headers, json=payload, timeout=30)

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully called LLM API. Usage: {result.get('usage', {})}")
                    return result
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limited. Waiting {wait_time} seconds before retry {attempt + 1}/{retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"API call failed with status {response.status_code}: {response.text}")
                    if attempt < retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise Exception(f"API call failed after {retries} retries: {response.status_code} - {response.text}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {str(e)}")
                if attempt < retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Request failed after {retries} retries: {str(e)}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                raise Exception(f"Failed to parse JSON response: {str(e)}")

        raise Exception("Max retries exceeded")

    def extract_text_response(self, response: Dict) -> str:
        """
        Extract the text response from the API response.

        Args:
            response (Dict): Full API response

        Returns:
            str: Extracted text content
        """
        try:
            return response["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract text from response: {str(e)}")
            logger.error(f"Response structure: {json.dumps(response, indent=2)}")
            raise Exception(f"Failed to extract text from response: {str(e)}")

    def test_connection(self) -> bool:
        """
        Test the connection to the OpenRouter API.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            test_prompt = "Hello, this is a test message."
            test_system_prompt = "You are a helpful assistant. Respond briefly."

            response = self.call_llm(
                prompt=test_prompt,
                system_prompt=test_system_prompt,
                max_tokens=50,
                temperature=0.5
            )

            text_response = self.extract_text_response(response)
            logger.info(f"Connection test successful. Response: {text_response}")
            return True

        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False


# Convenience function for easy access
def call_llm(prompt: str, system_prompt: str = None, **kwargs) -> Dict:
    """
    Convenience function to call the LLM without creating a client instance.

    Args:
        prompt (str): The user prompt to send to the LLM
        system_prompt (str): System prompt to guide the LLM's behavior
        **kwargs: Additional arguments to pass to the call_llm method

    Returns:
        Dict: Response from the LLM
    """
    client = OpenRouterClient()
    return client.call_llm(prompt, system_prompt, **kwargs)
