"""
Pydantic schemas for Trigger Mechanism API endpoints.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TriggerResponse(BaseModel):
    """Single trigger response."""
    trigger_id: str
    persona_id: str
    trigger_type: str
    message: str
    confidence_score: float
    timing: str
    talking_point: Optional[str] = None
    is_active: bool = True
    is_read: bool = False
    created_at: datetime


class TriggerListResponse(BaseModel):
    """List of triggers."""
    triggers: List[TriggerResponse]
    total: int
