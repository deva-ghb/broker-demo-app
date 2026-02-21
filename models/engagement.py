"""
Engagement event MongoDB document model.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class EngagementEvent(BaseModel):
    """Individual engagement event from client-side tracking."""
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    tracking_id: str
    persona_id: Optional[str] = None
    session_id: Optional[str] = None

    # Event details
    event_type: str  # "page_view" | "section_focus" | "cta_click" | "session_end" | "scroll_depth"
    payload: Dict[str, Any] = Field(default_factory=dict)
    # payload examples:
    #   section_focus: {"section": "payment_plans", "dwell_seconds": 45.2}
    #   scroll_depth: {"depth_percent": 85}
    #   cta_click: {"cta_type": "call_broker"}

    timestamp: datetime = Field(default_factory=datetime.utcnow)


# MongoDB collection name
ENGAGEMENT_COLLECTION = "engagement_events"
