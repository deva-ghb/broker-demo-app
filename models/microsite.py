"""
Microsite MongoDB document model.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class MicrositeDocument(BaseModel):
    """Generated microsite record."""
    microsite_id: str = Field(default_factory=lambda: f"ms_{uuid.uuid4().hex[:8]}")
    persona_id: str
    property_id: str
    tracking_id: str = Field(default_factory=lambda: f"trk_{uuid.uuid4().hex[:8]}")

    # Content
    html_content: str = ""
    url_slug: str = ""  # The unique slug for serving

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


# MongoDB collection name
MICROSITE_COLLECTION = "microsites"
