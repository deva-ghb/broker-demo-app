"""
Pydantic schemas for Recommendation API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class RecommendationRequest(BaseModel):
    """Request to get property recommendations."""
    persona_id: Optional[str] = None
    persona_json: Optional[Dict[str, Any]] = None


class RecommendationResponse(BaseModel):
    """Response from recommendation endpoint."""
    property_ids: List[str]
    filter_criteria: Optional[Dict[str, Any]] = None
