"""
Pydantic schemas for Engagement Tracker API endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class EngagementEventRequest(BaseModel):
    """Single engagement event."""
    event_type: str  # "page_view" | "section_focus" | "cta_click" | "session_end" | "scroll_depth"
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[str] = None


class EngagementBatchRequest(BaseModel):
    """Batch of engagement events."""
    tracking_id: str
    session_id: Optional[str] = None
    events: List[EngagementEventRequest]


class EngagementSummary(BaseModel):
    """Aggregated engagement summary for a tracking ID."""
    tracking_id: str
    persona_id: Optional[str] = None
    total_page_views: int = 0
    return_visit_count: int = 0
    max_scroll_depth: float = 0.0
    section_dwell_times: Dict[str, float] = Field(default_factory=dict)
    high_dwell_sections: List[str] = Field(default_factory=list)
    cta_clicks: int = 0
    last_active: Optional[datetime] = None
