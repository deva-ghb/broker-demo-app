"""
Trigger MongoDB document model.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class TriggerDocument(BaseModel):
    """AI-generated follow-up trigger for the broker."""
    trigger_id: str = Field(default_factory=lambda: f"trig_{uuid.uuid4().hex[:8]}")
    persona_id: str
    tracking_id: Optional[str] = None

    # Trigger details
    trigger_type: str  # "high_intent" | "specific_interest" | "completion"
    message: str  # Human-readable alert
    confidence_score: float = 0.0

    # Action guidance
    timing: str = "Call Now"  # "Call Now" | "Wait 2 Hours" etc.
    talking_point: Optional[str] = None  # Specific hook for the broker

    # State
    is_active: bool = True
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


# MongoDB collection name
TRIGGER_COLLECTION = "triggers"
