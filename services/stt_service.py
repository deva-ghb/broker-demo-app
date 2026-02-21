"""
Speech-to-Text service using OpenAI Whisper API.
"""
import os
import io
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
    return bool(os.getenv("OPENAI_API_KEY"))
