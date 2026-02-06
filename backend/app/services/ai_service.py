"""
AI Service for Mistral API integration.
Handles all AI-related operations including chat completions and streaming.
"""

from typing import Optional, Dict, Any, AsyncGenerator
import json
import time
from datetime import datetime
import httpx

from app.core.config import settings
from app.core.logging_config import get_logger
from app.schemas.conversation import ChatRequest, MessageResponse

logger = get_logger(__name__)


class AIService:
    """
    Service for interacting with Mistral AI API.
    Provides methods for chat completions and streaming responses.
    """

    def __init__(self):
        self.api_key = settings.MISTRAL_API_KEY
        self.api_url = settings.MISTRAL_API_URL
        self.default_model = settings.MISTRAL_MODEL
        self.default_max_tokens = settings.MISTRAL_MAX_TOKENS
        self.default_temperature = settings.MISTRAL_TEMPERATURE
        self.timeout = settings.MISTRAL_TIMEOUT

    def _prepare_messages(
        self,
        conversation_messages: list,
        system_prompt: Optional[str] = None
    ) -> list:
        """
        Prepare messages for Mistral API format.

        Args:
            conversation_messages: List of conversation messages
            system_prompt: Optional system prompt

        Returns:
            List of formatted messages
        """
        messages = []

        # Add system prompt
        system_text = system_prompt or settings.DEFAULT_SYSTEM_PROMPT
        messages.append({
            "role": "system",
            "content": system_text
        })

        # Add conversation messages
        for msg in conversation_messages:
            messages.append({
                "role": msg.get("role"),
                "content": msg.get("content")
            })

        return messages

    async def chat_completion(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get a chat completion from Mistral AI.

        Args:
            messages: List of conversation messages
            model: Model to use (defaults to configured model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional API parameters

        Returns:
            Dictionary with response data

        Raises:
            httpx.HTTPError: If API request fails
        """
        start_time = time.time()

        request_data = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.default_temperature,
            "max_tokens": max_tokens or self.default_max_tokens,
            **kwargs
        }

        logger.info(f"Sending chat completion request to Mistral API - Model: {request_data['model']}")
        logger.debug(f"Request params - temp: {request_data['temperature']}, max_tokens: {request_data['max_tokens']}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data
                )

                response.raise_for_status()
                response_data = response.json()

            processing_time_ms = int((time.time() - start_time) * 1000)
            logger.info(f"Chat completion successful - Processing time: {processing_time_ms}ms")

            # Extract response content
            assistant_content = response_data["choices"][0]["message"]["content"]
            usage = response_data.get("usage", {})
            finish_reason = response_data["choices"][0].get("finish_reason")

            return {
                "content": assistant_content,
                "usage": usage,
                "finish_reason": finish_reason,
                "model": response_data.get("model", request_data["model"]),
                "processing_time_ms": processing_time_ms
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Mistral API HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Mistral API request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in chat completion: {str(e)}")
            raise

    async def chat_completion_stream(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Get a streaming chat completion from Mistral AI.

        Args:
            messages: List of conversation messages
            model: Model to use (defaults to configured model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional API parameters

        Yields:
            Dictionaries with chunk data

        Raises:
            httpx.HTTPError: If API request fails
        """
        start_time = time.time()

        request_data = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.default_temperature,
            "max_tokens": max_tokens or self.default_max_tokens,
            "stream": True,
            **kwargs
        }

        logger.info(f"Sending streaming chat completion request to Mistral API - Model: {request_data['model']}")
        logger.debug(f"Request params - temp: {request_data['temperature']}, max_tokens: {request_data['max_tokens']}")

        full_response = ""
        chunk_count = 0

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue

                        if line.startswith("data: "):
                            data_str = line[6:].strip()

                            # Check for stream end
                            if data_str == "[DONE]":
                                processing_time_ms = int((time.time() - start_time) * 1000)
                                logger.info(
                                    f"Streaming completed - Chunks: {chunk_count}, "
                                    f"Length: {len(full_response)}, "
                                    f"Time: {processing_time_ms}ms"
                                )
                                yield {
                                    "type": "done",
                                    "full_response": full_response,
                                    "processing_time_ms": processing_time_ms
                                }
                                break

                            try:
                                data = json.loads(data_str)

                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})

                                    if "content" in delta:
                                        text = delta["content"]
                                        full_response += text
                                        chunk_count += 1

                                        yield {
                                            "type": "content",
                                            "text": text
                                        }

                                    # Check for finish reason
                                    finish_reason = data["choices"][0].get("finish_reason")
                                    if finish_reason:
                                        yield {
                                            "type": "finish",
                                            "reason": finish_reason
                                        }

                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse streaming chunk: {e}")
                                continue

        except httpx.HTTPStatusError as e:
            logger.error(f"Mistral API streaming HTTP error: {e.response.status_code}")
            yield {
                "type": "error",
                "message": f"API error: {e.response.status_code}",
                "details": str(e)
            }
        except httpx.RequestError as e:
            logger.error(f"Mistral API streaming request error: {str(e)}")
            yield {
                "type": "error",
                "message": "Request failed",
                "details": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error in streaming: {str(e)}")
            yield {
                "type": "error",
                "message": "Unexpected error",
                "details": str(e)
            }

    async def generate_title(self, first_message: str) -> str:
        """
        Generate a conversation title from the first message.

        Args:
            first_message: First message in conversation

        Returns:
            Generated title string
        """
        # Simple title generation - take first 50 chars
        title = first_message.strip()

        # Remove newlines
        title = title.replace("\n", " ")

        # Truncate if too long
        if len(title) > 50:
            title = title[:50] + "..."

        # If empty, use default
        if not title:
            title = f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"

        return title

    async def validate_api_key(self) -> bool:
        """
        Validate that the API key is configured and working.

        Returns:
            True if API key is valid, False otherwise
        """
        if not self.api_key:
            logger.error("Mistral API key not configured")
            return False

        try:
            # Try a simple API call
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hi"}
            ]

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.default_model,
                        "messages": messages,
                        "max_tokens": 10
                    }
                )

                response.raise_for_status()
                logger.info("Mistral API key validation successful")
                return True

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.error("Mistral API key is invalid")
            else:
                logger.error(f"Mistral API validation error: {e.response.status_code}")
            return False
        except Exception as e:
            logger.error(f"Mistral API validation failed: {str(e)}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the configured AI model.

        Returns:
            Dictionary with model information
        """
        return {
            "provider": "Mistral AI",
            "model": self.default_model,
            "api_url": self.api_url,
            "max_tokens": self.default_max_tokens,
            "temperature": self.default_temperature,
            "timeout": self.timeout
        }


# Global AI service instance
ai_service = AIService()


# Convenience functions
async def chat_completion(
    messages: list,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for chat completion.
    """
    return await ai_service.chat_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )


async def chat_completion_stream(
    messages: list,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Convenience function for streaming chat completion.
    """
    async for chunk in ai_service.chat_completion_stream(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    ):
        yield chunk
