"""
Text-to-Speech service using Kyutai Pocket TTS API.
"""
import os
import httpx
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

TTS_BASE_URL = os.getenv("TTS_BASE_URL", "https://ai-tts.treppanliving.ae")


async def text_to_speech_stream(text: str) -> AsyncGenerator[bytes, None]:
    """
    Convert text to speech using Pocket TTS API.
    Returns an async generator that yields audio chunks.

    Args:
        text: The text to convert to speech

    Yields:
        Audio data chunks (bytes)
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream(
                "POST",
                f"{TTS_BASE_URL}/tts",
                data={"text": text},
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk

    except httpx.HTTPError as e:
        logger.error(f"TTS API error: {e}")
        raise Exception(f"Failed to generate speech: {str(e)}")


async def text_to_speech(text: str) -> bytes:
    """
    Convert text to speech and return complete audio data.

    Args:
        text: The text to convert to speech

    Returns:
        Complete audio data as bytes
    """
    audio_chunks = []
    async for chunk in text_to_speech_stream(text):
        audio_chunks.append(chunk)
    return b"".join(audio_chunks)


async def check_tts_health() -> bool:
    """
    Check if TTS service is available.

    Returns:
        True if service is healthy, False otherwise
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{TTS_BASE_URL}/health")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"TTS health check failed: {e}")
        return False
