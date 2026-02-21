"""
Microsite Builder service — generates personalized, trackable microsites
by merging Buyer Persona with Property Assets from the Knowledge Base.
"""
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from jinja2 import Template
from pathlib import Path

from services.ai_client import ai_client
from services.database import get_collection
from services.knowledge_base import get_property_context
from models.persona import PERSONA_COLLECTION
from models.property import PROPERTY_COLLECTION
from models.microsite import MicrositeDocument, MICROSITE_COLLECTION
from settings import settings


async def build_microsite(persona_id: str, property_id: str) -> Dict[str, Any]:
    """
    Build a personalized microsite for a given persona and property.
    Returns: { microsite_url, tracking_id, microsite_id }
    """
    # 1. Fetch persona
    persona_col = get_collection(PERSONA_COLLECTION)
    persona = await persona_col.find_one({"persona_id": persona_id})
    if not persona:
        raise ValueError(f"Persona {persona_id} not found")
    persona.pop("_id", None)

    # 2. Fetch property
    property_col = get_collection(PROPERTY_COLLECTION)
    prop = await property_col.find_one({"property_id": property_id})
    if not prop:
        raise ValueError(f"Property {property_id} not found")
    prop.pop("_id", None)

    # 3. Filter assets based on persona interests
    filtered_assets = _filter_assets(prop.get("assets", []), persona)

    # 4. Generate persona-specific captions for images
    captioned_assets = await _contextualize_assets(filtered_assets, persona)

    # 5. Render HTML
    html_content = _render_microsite_html(persona, prop, captioned_assets)

    # 6. Create and persist microsite document
    microsite = MicrositeDocument(
        persona_id=persona_id,
        property_id=property_id,
        html_content=html_content,
        url_slug=persona_id,  # Use persona_id as slug for tracking
    )

    ms_col = get_collection(MICROSITE_COLLECTION)
    await ms_col.insert_one(microsite.model_dump())

    microsite_url = f"{settings.APP_BASE_URL}/m/{microsite.url_slug}"

    return {
        "microsite_url": microsite_url,
        "tracking_id": microsite.tracking_id,
        "microsite_id": microsite.microsite_id,
    }


def _filter_assets(assets: List[Dict], persona: Dict) -> List[Dict]:
    """Filter assets based on persona's key_interests and ignored_features."""
    key_interests = [k.lower() for k in persona.get("key_interests", [])]
    ignored = [i.lower() for i in persona.get("ignored_features", [])]

    if not key_interests and not ignored:
        return assets

    filtered = []
    for asset in assets:
        desc = asset.get("description", "").lower()
        content = asset.get("content", "").lower()
        combined = f"{desc} {content}"

        # Skip if matches ignored features
        if any(ig in combined for ig in ignored):
            continue

        filtered.append(asset)

    return filtered if filtered else assets  # Fallback to all if filter is too aggressive


async def _contextualize_assets(assets: List[Dict], persona: Dict) -> List[Dict]:
    """Generate persona-specific captions for image assets using AI."""
    if not assets:
        return assets

    persona_type = persona.get("persona_type", "General")
    motivation = persona.get("primary_motivation", "")

    contextualized = []
    for asset in assets:
        new_asset = dict(asset)
        if asset.get("type") == "image":
            # Generate contextual caption
            prompt = f"""Given a buyer who is a {persona_type} motivated by "{motivation}", 
write a short, compelling caption (max 10 words) for this property image: "{asset.get('description', '')}"
Return ONLY the caption text, nothing else."""

            try:
                caption, _, _ = ai_client.completion(
                    [{"role": "user", "content": prompt}]
                )
                new_asset["contextual_caption"] = caption.strip()
            except Exception:
                new_asset["contextual_caption"] = asset.get("description", "")

        contextualized.append(new_asset)

    return contextualized


def _render_microsite_html(persona: Dict, prop: Dict, assets: List[Dict]) -> str:
    """Render the microsite HTML from the Jinja2 template."""
    template_path = Path(__file__).parent.parent / "templates" / "microsite.html"

    if template_path.exists():
        template_str = template_path.read_text()
    else:
        template_str = _get_fallback_template()

    template = Template(template_str)

    return template.render(
        persona=persona,
        property=prop,
        assets=assets,
        brand_color=prop.get("brand_color", "#1a73e8"),
        broker_name=prop.get("broker_name", "Your Broker"),
        broker_phone=prop.get("broker_phone", ""),
        broker_email=prop.get("broker_email", ""),
        broker_logo_url=prop.get("broker_logo_url", ""),
        tracking_id=persona.get("persona_id", ""),
        base_url=settings.APP_BASE_URL,
    )


async def get_microsite_html(persona_id: str) -> Optional[str]:
    """Retrieve microsite HTML by persona_id (url_slug)."""
    ms_col = get_collection(MICROSITE_COLLECTION)
    doc = await ms_col.find_one({"url_slug": persona_id, "is_active": True})
    if doc:
        return doc.get("html_content")
    return None


def _get_fallback_template() -> str:
    """Inline fallback template if the file is missing."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ property.get('name', 'Property') }} | {{ broker_name }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #f8f9fa; color: #333; }
        .sticky-cta { position: fixed; top: 0; width: 100%; z-index: 1000; background: {{ brand_color }};
            padding: 12px 20px; display: flex; align-items: center; justify-content: space-between; }
        .sticky-cta a { color: #fff; text-decoration: none; font-weight: 600; font-size: 16px; }
        .sticky-cta .broker-info { color: rgba(255,255,255,0.9); font-size: 13px; }
        .content { margin-top: 60px; padding: 20px; max-width: 600px; margin-left: auto; margin-right: auto; }
        .hero { background: {{ brand_color }}; color: #fff; padding: 40px 20px; border-radius: 12px; margin-bottom: 20px; }
        .hero h1 { font-size: 24px; margin-bottom: 8px; }
        .hero p { opacity: 0.9; font-size: 14px; }
        .section { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .section h2 { font-size: 18px; color: {{ brand_color }}; margin-bottom: 12px; }
        .section p { font-size: 14px; line-height: 1.6; }
        .asset-img { width: 100%; border-radius: 8px; margin: 12px 0; }
        .asset-caption { font-size: 13px; color: #666; font-style: italic; margin-bottom: 12px; }
        .tag { display: inline-block; background: {{ brand_color }}15; color: {{ brand_color }};
            padding: 4px 12px; border-radius: 20px; font-size: 12px; margin: 4px; }
    </style>
</head>
<body>
    <div class="sticky-cta">
        <a href="tel:{{ broker_phone }}">📞 Talk to {{ broker_name }}</a>
        <span class="broker-info">Your exclusive broker</span>
    </div>
    <div class="content">
        <div class="hero">
            <h1>{{ property.get('name', 'Exclusive Property') }}</h1>
            <p>{{ property.get('location', '') }} | {{ property.get('developer', '') }}</p>
            {% if persona.get('primary_motivation') %}
            <p style="margin-top: 12px; font-weight: 500;">{{ persona.get('ai_recommended_angle', '') }}</p>
            {% endif %}
        </div>
        {% for asset in assets %}
        <div class="section" data-section="{{ asset.get('description', 'section') | replace(' ', '_') | lower }}">
            {% if asset.get('type') == 'image' %}
            <img src="{{ asset.get('url', '') }}" alt="{{ asset.get('description', '') }}" class="asset-img">
            <p class="asset-caption">{{ asset.get('contextual_caption', asset.get('description', '')) }}</p>
            {% else %}
            <h2>{{ asset.get('description', 'Details') }}</h2>
            <p>{{ asset.get('content', '') }}</p>
            {% endif %}
        </div>
        {% endfor %}
        {% if property.get('usps') %}
        <div class="section">
            <h2>Key Highlights</h2>
            {% for usp in property.get('usps', []) %}
            <span class="tag">{{ usp }}</span>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    <meta name="tracking-id" content="{{ tracking_id }}">
    <script src="{{ base_url }}/static/tracker.js"></script>
</body>
</html>"""
