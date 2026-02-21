"""
Persona MongoDB document model.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class DemographicContext(BaseModel):
    nationality: Optional[str] = None
    language_preference: Optional[str] = "English"
    residency_status: Optional[str] = None


class EngagementSignals(BaseModel):
    high_dwell_sections: List[str] = Field(default_factory=list)
    return_visit_count: int = 0
    last_active_timestamp: Optional[datetime] = None
    total_page_views: int = 0
    max_scroll_depth: float = 0.0
    section_dwell_times: Dict[str, float] = Field(default_factory=dict)


class PersonaDocument(BaseModel):
    """Full Persona document stored in MongoDB."""
    persona_id: str = Field(default_factory=lambda: f"prs_{uuid.uuid4().hex[:8]}")
    broker_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Profile
    persona_type: Optional[str] = None  # e.g. "Investor", "End-User", "Family"
    demographic_context: DemographicContext = Field(default_factory=DemographicContext)
    primary_motivation: Optional[str] = None
    key_interests: List[str] = Field(default_factory=list)
    ignored_features: List[str] = Field(default_factory=list)

    # Engagement (updated by tracker)
    engagement_signals: EngagementSignals = Field(default_factory=EngagementSignals)

    # AI-generated insights
    ai_recommended_angle: Optional[str] = None
    trust_level_score: int = 50
    next_best_action: Optional[str] = None

    # Conversation state
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    session_status: str = "collecting"  # "collecting" | "complete"


# MongoDB collection name
PERSONA_COLLECTION = "personas"
