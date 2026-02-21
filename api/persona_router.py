"""
Persona Builder API router.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional

from schemas.persona_schemas import (
    TextChatRequest,
    TextChatResponse,
    PersonaResponse,
    PersonaListResponse,
)
from services.persona_service import handle_text_chat, get_persona, list_personas

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
    Accepts audio input, returns audio response + transcript.
    
    NOTE: Full audio STT/TTS integration requires Azure Speech Services.
    Currently falls back to text processing with a placeholder.
    """
    # Read audio data
    audio_data = await audio_blob.read()

    # TODO: Integrate Azure Speech STT here
    # For now, return a placeholder indicating audio support is pending
    # In production: audio_data → Azure STT → text → AI → Azure TTS → audio response

    return {
        "session_id": session_id or "new_session",
        "transcript": "Audio processing is being set up. Please use text chat for now.",
        "session_status": "collecting",
        "persona_id": None,
        "message": "Audio-to-audio support requires Azure Speech Services configuration. Use /text-chat endpoint.",
    }


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
