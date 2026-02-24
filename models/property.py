"""
Property MongoDB document model.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


class PropertyAsset(BaseModel):
    """Individual asset (text or image) belonging to a property."""
    type: str  # "text" | "image"
    content: str  # The text content or image filename
    description: str  # Description of the asset
    url: Optional[str] = None  # URL if the asset is an image


class PropertyDocument(BaseModel):
    """Property document stored in MongoDB, synced with Qdrant for embeddings."""
    property_id: str = Field(default_factory=lambda: f"prop_{uuid.uuid4().hex[:8]}")
    name: str
    developer: Optional[str] = None
    location: Optional[str] = None
    property_type: Optional[str] = None  # e.g. "Apartment", "Villa", "Townhouse"

    # Assets
    assets: List[PropertyAsset] = Field(default_factory=list)

    # USPs and metadata for knowledge base
    usps: List[str] = Field(default_factory=list)
    price_start_aed_in_million: Optional[float] = None
    price_end_aed_in_million: Optional[float] = None
    payment_plans: Optional[str] = None
    
    # Vector fields for Qdrant named vectors
    description_vector: Optional[List[float]] = None
    amenities_vector: Optional[List[float]] = None
    golden_visa_eligible: bool = False
    projected_roi: Optional[str] = None

    # Broker branding
    broker_name: Optional[str] = None
    broker_logo_url: Optional[str] = None
    broker_phone: Optional[str] = None
    broker_email: Optional[str] = None
    brand_color: str = "#1a73e8"

    # ── Clone template structured data (optional) ──
    hero_video_url: Optional[str] = None
    hero_logo_url: Optional[str] = None
    brand_ambassador: Optional[Dict[str, Any]] = None
    usp_cards: Optional[List[Dict[str, Any]]] = None
    a_la_carte_services: Optional[List[str]] = None
    wellness_features: Optional[List[Dict[str, Any]]] = None
    premium_living_services: Optional[List[str]] = None
    amenities_grid: Optional[List[Dict[str, Any]]] = None
    location_map_embed: Optional[str] = None
    proximity: Optional[Dict[str, Any]] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# MongoDB collection name
PROPERTY_COLLECTION = "properties"
