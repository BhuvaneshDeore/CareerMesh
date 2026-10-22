"""
services/llm_provider.py - LLM Provider Interface and Integrations

Provides:
- BaseLLMProvider interface
- Concrete HTTP/REST-based client supporting Google Gemini and OpenAI compatible endpoints
- Robust error handling for rate limits, timeouts, and auth errors
- Never silently switches modes without clear user notification
"""

import json
import logging
from typing import Optional, Dict, Any
from config import LLM_PROVIDER, LLM_API_KEY, LLM_MODEL

logger = logging.getLogger("CareerMesh.LLMProvider")


class LLMConfigurationError(Exception):
    """Raised when LLM configuration is missing or invalid."""
    pass


class LLMExecutionError(Exception):
    """Raised when an external LLM request fails."""
    pass


class BaseLLMProvider:
    """Abstract interface for LLM providers."""

    def is_available(self) -> bool:
        raise NotImplementedError

    def generate_json(self, prompt: str, schema_description: str) -> Dict[str, Any]:
        raise NotImplementedError


class GeminiRESTProvider(BaseLLMProvider):
    """
    Direct HTTP client for Google Gemini API using standard httpx/requests.
    Avoids heavy unnecessary SDK dependencies while fully supporting Gemini 1.5/2.0.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate_json(self, prompt: str, schema_description: str) -> Dict[str, Any]:
        if not self.is_available():
            raise LLMConfigurationError("Gemini API key is not configured. Set LLM_API_KEY in .env.")

        import httpx

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"{prompt}\n\nYou MUST return valid JSON adhering strictly to this schema: {schema_description}. Return JSON ONLY without markdown backticks."
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }

        try:
            response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
            if response.status_code == 401 or response.status_code == 403:
                raise LLMExecutionError(f"Authentication failed (HTTP {response.status_code}). Check your LLM_API_KEY.")
            elif response.status_code == 429:
                raise LLMExecutionError("Gemini rate limit exceeded (HTTP 429). Please retry after a moment.")
            elif response.status_code != 200:
                raise LLMExecutionError(f"Gemini API returned HTTP {response.status_code}: {response.text}")

            result_json = response.json()
            candidates = result_json.get("candidates", [])
            if not candidates:
                raise LLMExecutionError("Gemini returned empty candidates in response.")

            text_content = candidates[0]["content"]["parts"][0]["text"].strip()
            # Clean possible markdown wrap
            if text_content.startswith("```json"):
                text_content = text_content[7:]
            if text_content.startswith("```"):
                text_content = text_content[3:]
            if text_content.endswith("```"):
                text_content = text_content[:-3]

            return json.loads(text_content.strip())

        except httpx.TimeoutException:
            raise LLMExecutionError("Gemini API request timed out after 30 seconds.")
        except json.JSONDecodeError as jde:
            raise LLMExecutionError(f"Failed to parse LLM response as JSON: {str(jde)}")
        except Exception as e:
            if isinstance(e, (LLMConfigurationError, LLMExecutionError)):
                raise
            raise LLMExecutionError(f"Unexpected error communicating with Gemini API: {str(e)}")


class OpenAIPROVIDER(BaseLLMProvider):
    """
    Direct HTTP client for OpenAI-compatible endpoints using httpx.
    """

    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate_json(self, prompt: str, schema_description: str) -> Dict[str, Any]:
        if not self.is_available():
            raise LLMConfigurationError("OpenAI API key is not configured. Set LLM_API_KEY in .env.")

        import httpx

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": f"You are a career assistant agent. Return strictly valid JSON conforming to: {schema_description}",
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        try:
            response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
            if response.status_code == 401:
                raise LLMExecutionError("OpenAI authentication failed. Invalid LLM_API_KEY.")
            elif response.status_code == 429:
                raise LLMExecutionError("OpenAI rate limit or quota exceeded.")
            elif response.status_code != 200:
                raise LLMExecutionError(f"OpenAI API returned HTTP {response.status_code}: {response.text}")

            result_json = response.json()
            content = result_json["choices"][0]["message"]["content"]
            return json.loads(content)

        except httpx.TimeoutException:
            raise LLMExecutionError("OpenAI API request timed out after 30 seconds.")
        except json.JSONDecodeError as jde:
            raise LLMExecutionError(f"Failed to parse OpenAI JSON response: {str(jde)}")
        except Exception as e:
            if isinstance(e, (LLMConfigurationError, LLMExecutionError)):
                raise
            raise LLMExecutionError(f"Unexpected error communicating with OpenAI API: {str(e)}")


def get_configured_llm_provider() -> Optional[BaseLLMProvider]:
    """
    Returns the configured LLM provider if valid credentials exist, else None.
    """
    provider_name = LLM_PROVIDER.lower()
    if not provider_name or provider_name == "none":
        return None

    if provider_name in ("gemini", "google"):
        return GeminiRESTProvider(api_key=LLM_API_KEY, model_name=LLM_MODEL or "gemini-1.5-flash")
    elif provider_name in ("openai", "chatgpt"):
        return OpenAIPROVIDER(api_key=LLM_API_KEY, model_name=LLM_MODEL or "gpt-4o-mini")
    else:
        logger.warning(f"Unknown LLM provider '{provider_name}'. Supported: 'gemini', 'openai'.")
        return None
