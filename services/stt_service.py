"""
Speech-to-Text service using OpenAI Whisper API.
"""
import os
import io
import logging
from openai import AsyncOpenAI, AsyncAzureOpenAI
from settings import settings

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = None
if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
    client = AsyncAzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
    )
    # Note: Azure OpenAI Whisper deployment name must be configured if different from standard whisper-1
elif settings.OPENAI_API_KEY:
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def speech_to_text(audio_data: bytes, filename: str = "audio.webm") -> str:
    """
    Convert speech audio to text using OpenAI Whisper.

    Args:
        audio_data: Audio file data in bytes
        filename: Original filename (helps determine format)

    Returns:
        Transcribed text
    """
    try:
        if not client:
            raise Exception("STT service is not configured (missing AZURE_OPENAI_API_KEY or OPENAI_API_KEY)")

        # Create a file-like object from bytes
        audio_file = io.BytesIO(audio_data)
        audio_file.name = filename

        # Use OpenAI Whisper API
        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en"  # Can be made dynamic based on user preference
        )

        return transcript.text

    except Exception as e:
        logger.error(f"STT error: {e}")
        # Fallback: return empty string or error message
        raise Exception(f"Failed to transcribe audio: {str(e)}")


async def check_stt_availability() -> bool:
    """
    Check if STT service (OpenAI API) is available.

    Returns:
        True if OPENAI_API_KEY is configured, False otherwise
    """
    return bool((settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT) or settings.OPENAI_API_KEY)
