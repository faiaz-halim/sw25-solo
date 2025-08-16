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

    def call_llm(self, prompt: str, system_prompt: str = None, model: str = None,
                 temperature: float = 0.7, retries: int = 3, model_priority_list: list = None) -> Dict:
        """
        Call the LLM through OpenRouter API with model fallback support.

        Args:
            prompt (str): The user prompt to send to the LLM
            system_prompt (str): System prompt to guide the LLM's behavior
            model (str): The specific model to use (if None, will use priority list)
            temperature (float): Temperature for response randomness (0.0 to 1.0)
            retries (int): Number of retry attempts for failed requests
            model_priority_list (list): List of models to try in order of preference

        Returns:
            Dict: Response from the LLM containing the generated text and metadata

        Raises:
            Exception: If the API call fails after all retries and all models
        """
        # Default priority list if none provided
        if model_priority_list is None:
            model_priority_list = [
                "cognitivecomputations/dolphin3.0-mistral-24b:free",
                "mistralai/mistral-small-24b-instruct-2501:free",
                "meta-llama/llama-3.3-70b-instruct:free",
                "qwen/qwen3-coder:free",
                "qwen/qwen3-30b-a3b:free"
            ]

        # If specific model is provided, use it
        models_to_try = [model] if model else model_priority_list

        last_exception = None

        # Try each model in order
        for current_model in models_to_try:
            messages = []

            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            # Add user prompt
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": current_model,
                "messages": messages,
                "temperature": temperature
            }

            url = f"{self.base_url}/chat/completions"

            # Log the request for debugging
            logger.info(f"Calling LLM API with model: {current_model}")
            logger.debug(f"System prompt: {system_prompt}")
            logger.debug(f"User prompt: {prompt}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

            for attempt in range(retries + 1):
                try:
                    response = requests.post(url, headers=self.headers, json=payload, timeout=30)

                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"Successfully called LLM API with model {current_model}. Usage: {result.get('usage', {})}")
                        # Log the response content
                        if result.get('choices'):
                            response_content = result['choices'][0].get('message', {}).get('content', '')
                            logger.debug(f"LLM Response: {response_content}")
                        return result
                    elif response.status_code == 429:
                        # Rate limited - wait and retry
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"Rate limited with model {current_model}. Waiting {wait_time} seconds before retry {attempt + 1}/{retries}")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"API call failed with model {current_model} status {response.status_code}: {response.text}")
                        if attempt < retries:
                            wait_time = 2 ** attempt
                            logger.warning(f"Retrying in {wait_time} seconds...")
                            time.sleep(wait_time)
                            continue
                        else:
                            last_exception = Exception(f"API call failed after {retries} retries with model {current_model}: {response.status_code} - {response.text}")
                            break  # Break inner retry loop to try next model

                except requests.exceptions.RequestException as e:
                    logger.error(f"Request failed with model {current_model}: {str(e)}")
                    if attempt < retries:
                        wait_time = 2 ** attempt
                        logger.warning(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        last_exception = Exception(f"Request failed after {retries} retries with model {current_model}: {str(e)}")
                        break  # Break inner retry loop to try next model
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response with model {current_model}: {str(e)}")
                    last_exception = Exception(f"Failed to parse JSON response with model {current_model}: {str(e)}")
                    break  # Break inner retry loop to try next model

            # If we get here, this model failed after all retries. Continue to next model.
            logger.warning(f"All retries exhausted for model {current_model}. Trying next model in priority list.")
            continue

        # If we get here, all models failed
        raise Exception(f"All models failed after retries. Last error: {str(last_exception)}")

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
