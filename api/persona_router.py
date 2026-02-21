"""
Persona Builder API router.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional
import logging

from schemas.persona_schemas import (
    TextChatRequest,
    TextChatResponse,
    PersonaResponse,
    PersonaListResponse,
)
from services.persona_service import handle_text_chat, get_persona, list_personas
from services.stt_service import speech_to_text
from services.tts_service import text_to_speech_stream

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/persona", tags=["Persona Builder"])


@router.post("/text-chat", response_model=TextChatResponse)
async def text_chat(request: TextChatRequest):
    """
    Text-based persona building chat.
    Send a message, get an AI reply.
    When session_status is 'complete', the persona_id is returned.
    """
    result = await handle_text_chat(
        message=request.message,
        session_id=request.session_id,
        broker_id=request.broker_id,
        property_id=request.property_id,
    )
    return TextChatResponse(**result)


@router.post("/audio-chat")
async def audio_chat(
    audio_blob: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    broker_id: Optional[str] = Form(None),
    property_id: Optional[str] = Form(None),
):
    """
    Audio-based persona building chat.
    Accepts audio input, returns JSON with transcript and text response.
    Use /tts endpoint to convert the reply to speech.

    Flow: Audio → STT (Whisper) → Text Chat → Reply
    """
    try:
        # Read audio data
        audio_data = await audio_blob.read()

        # Convert speech to text using Whisper
        logger.info(f"Transcribing audio (size: {len(audio_data)} bytes)")
        transcript = await speech_to_text(audio_data, audio_blob.filename or "audio.webm")
        logger.info(f"Transcript: {transcript}")

        # Process via text chat
        result = await handle_text_chat(
            message=transcript,
            session_id=session_id,
            broker_id=broker_id,
            property_id=property_id,
        )

        # Return transcript + chat response
        return {
            "session_id": result["session_id"],
            "transcript": transcript,
            "reply": result["reply"],
            "session_status": result["session_status"],
            "persona_id": result.get("persona_id"),
        }

    except Exception as e:
        logger.error(f"Audio chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Audio processing failed: {str(e)}"
        )


@router.post("/tts")
async def text_to_speech_endpoint(text: str = Form(...)):
    """
    Convert text to speech using Pocket TTS.
    Returns streaming audio response.
    """
    try:
        return StreamingResponse(
            text_to_speech_stream(text),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline",
                "Cache-Control": "no-cache",
            }
        )
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Text-to-speech failed: {str(e)}"
        )


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona_by_id(persona_id: str):
    """Retrieve a completed persona by ID."""
    persona = await get_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail=f"Persona {persona_id} not found")
    return PersonaResponse(**persona)


@router.get("/", response_model=PersonaListResponse)
async def list_all_personas(broker_id: Optional[str] = None, limit: int = 50):
    """List personas, optionally filtered by broker_id."""
    personas = await list_personas(broker_id=broker_id, limit=limit)
    return PersonaListResponse(
        personas=[PersonaResponse(**p) for p in personas],
        total=len(personas),
    )
