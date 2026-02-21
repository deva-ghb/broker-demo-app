"""
Persona MongoDB document model.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# The 7 Dimensions
class Identity(BaseModel):
    nationality: Optional[str] = None
    language_preference: Optional[str] = None
    residency_status: Optional[str] = None
    buyer_type: Optional[str] = None

class Motivation(BaseModel):
    primary_goal: Optional[str] = None
    urgency: Optional[str] = None
    secondary_goals: List[str] = Field(default_factory=list)

class Financial(BaseModel):
    budget_min: Optional[int] = 0
    budget_max: Optional[int] = 0
    payment_preference: Optional[str] = None
    is_flexible: bool = False

class Lifestyle(BaseModel):
    household_composition: Optional[str] = None
    lifestyle_tags: List[str] = Field(default_factory=list)
    must_have_amenities: List[str] = Field(default_factory=list)
    deal_breaker_features: List[str] = Field(default_factory=list)

class Engagement(BaseModel):
    trust_level: Optional[str] = None
    lead_source: Optional[str] = None
    prior_interactions_count: int = 0
    decision_makers: List[str] = Field(default_factory=list)

class PropertyFit(BaseModel):
    unit_type: Optional[str] = None
    floor_preference: Optional[str] = None
    view_preference: Optional[str] = None
    ready_vs_offplan: Optional[str] = None

class Communication(BaseModel):
    preferred_channel: Optional[str] = None
    best_time_to_reach: Optional[str] = None
    language_for_pitch: Optional[str] = None

class CompletenessScore(BaseModel):
    overall_score: float = 0.0
    dimension_scores: Dict[str, float] = Field(default_factory=dict)
    missing_dimensions: List[str] = Field(default_factory=list)
    is_complete: bool = False

class PersonaDocument(BaseModel):
    """Full Persona document stored in MongoDB."""
    persona_id: str = Field(default_factory=lambda: f"prs_{uuid.uuid4().hex[:10]}")
    broker_id: Optional[str] = None
    property_id: Optional[str] = None
    lead_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # The 7 Dimensions
    identity: Identity = Field(default_factory=Identity)
    motivation: Motivation = Field(default_factory=Motivation)
    financial: Financial = Field(default_factory=Financial)
    lifestyle: Lifestyle = Field(default_factory=Lifestyle)
    engagement: Engagement = Field(default_factory=Engagement)
    property_fit: PropertyFit = Field(default_factory=PropertyFit)
    communication: Communication = Field(default_factory=Communication)

    # Completeness Score
    completeness: CompletenessScore = Field(default_factory=CompletenessScore)

    # AI-generated insights
    ai_persona_label: Optional[str] = None
    ai_recommended_angle: Optional[str] = None
    ai_recommended_persona_type: Optional[str] = None
    next_best_action: Optional[str] = None
    trust_level_score: int = 50

    # Conversation state
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    session_status: str = "collecting"  # "collecting" | "complete" | "abandoned"

# MongoDB collection name
PERSONA_COLLECTION = "personas"
