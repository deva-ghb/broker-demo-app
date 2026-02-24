"""
Pydantic schemas for Persona Builder API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class TextChatRequest(BaseModel):
    """Request for text-based persona chat."""
    session_id: Optional[str] = None
    broker_id: Optional[str] = None
    property_id: Optional[str] = None
    message: str


class TextChatResponse(BaseModel):
    """Response from text-based persona chat."""
    session_id: str
    reply: str
    session_status: str  # "collecting" | "complete"
    persona_id: Optional[str] = None  # Set when status is "complete"


class AudioChatResponse(BaseModel):
    """Response metadata from audio-based persona chat."""
    session_id: str
    transcript: str  # AI's text response
    session_status: str
    persona_id: Optional[str] = None


class PersonaResponse(BaseModel):
    """Full persona response for GET endpoint — aligned with PersonaDocument."""
    persona_id: str
    broker_id: Optional[str] = None
    created_at: datetime

    # 7 Dimensions (matching PersonaDocument storage)
    identity: Dict = {}
    motivation: Dict = {}
    financial: Dict = {}
    lifestyle: Dict = {}
    engagement: Dict = {}
    property_fit: Dict = {}
    communication: Dict = {}

    # AI-generated insights
    ai_persona_label: Optional[str] = None
    ai_recommended_angle: Optional[str] = None
    ai_recommended_persona_type: Optional[str] = None
    next_best_action: Optional[str] = None
    trust_level_score: int = 50
    session_status: str = "collecting"


class PersonaListResponse(BaseModel):
    """List of personas."""
    personas: List[PersonaResponse]
    total: int
