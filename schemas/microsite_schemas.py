"""
Pydantic schemas for Microsite Builder API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class MicrositeBuildRequest(BaseModel):
    """Request to build a microsite."""
    persona_id: str
    property_id: str


class MicrositeBuildResponse(BaseModel):
    """Response from microsite build endpoint."""
    microsite_url: str
    tracking_id: str
    microsite_id: str
