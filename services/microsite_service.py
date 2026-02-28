"""
Microsite Builder service — generates personalized, trackable microsites
by merging Buyer Persona with Property Assets from the Knowledge Base.

AI Enrichment Pipeline:
  1. Fetch persona + property
  2. Filter assets (remove deal-breaker matches)
  3. AI Enrichment (single LLM call → hero headline, rewritten sections,
     curated USPs, objection handler, financial pitch)
  4. AI image captions
  5. Persona-driven section ordering
  6. Render + store HTML
"""
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from jinja2 import Template
from pathlib import Path
from pydantic import BaseModel

from services.ai_client import ai_client
from services.database import get_collection
from services.knowledge_base import get_property_context
from models.persona import PERSONA_COLLECTION
from models.property import PROPERTY_COLLECTION
from models.microsite import MicrositeDocument, MICROSITE_COLLECTION
from settings import settings


# ── Pydantic model for structured AI enrichment output ──────────

class EnrichedSection(BaseModel):
    section_key: str       # e.g., "overview", "amenities", "pricing", "roi", "golden_visa"
    heading: str           # rewritten heading
    content: str           # rewritten body copy

class EnrichedAmenity(BaseModel):
    name: str              # amenity name (must match a name from the amenities list)
    description: str       # 1-2 sentence persona-tailored description

class EnrichedMicrositeContent(BaseModel):
    hero_headline: str              # persona-specific tagline (max 10 words)
    hero_subheadline: str           # one-line supporting text (max 15 words)
    sections: List[EnrichedSection] # rewritten text sections
    curated_usps: List[str]         # top 5 most relevant USPs for this persona
    objection_handler_heading: str  # e.g., "Why Dubai Islands?"
    objection_handler_content: str  # 2-3 sentences addressing likely concerns
    financial_headline: str         # persona-framed financial heading
    financial_pitch: str            # 2-3 sentences reframing financials for this buyer
    cta_text: str = "Express Interest"          # persona-specific CTA button text (max 4 words)
    cta_heading: str = "Ready to Explore?"      # persona-specific CTA section heading
    highlighted_amenity_categories: List[str] = []  # categories to highlight: wellness, family, fitness, etc.
    top_amenities: List[EnrichedAmenity] = []   # top 4-6 amenities for showcase cards
    ambassador_desc: str = ""       # persona-tailored rewrite of brand ambassador blurb (same length as original)
    services_intro: str = ""        # persona-tailored 1-2 sentence intro for a-la-carte services


# ── Enrichment Prompt ───────────────────────────────────────────

ENRICHMENT_PROMPT = """You are a world-class real estate copywriter who writes with warmth and genuine care.
Your job: take generic property content and rewrite it so it speaks directly to THIS specific buyer,
making them feel understood and excited — like a trusted friend showing them their dream home.

## BUYER PERSONA
{persona_json}

## PROPERTY DATA
- Name: {property_name}
- Location: {property_location}
- Developer: {developer}
- Type: {property_type}
- Price: AED {price_start}M – {price_end}M
- USPs: {usps}

## ORIGINAL TEXT SECTIONS (to rewrite for this buyer)
{sections_json}

## YOUR TASK — Return this JSON structure:

1. **hero_headline**: A warm, punchy headline (max 10 words) that makes this buyer FEEL something.
   - NOT generic like "Luxury Living Awaits". Instead, speak to who they are:
     - For a wellness seeker: "Your Wellness Sanctuary on the Island"
     - For an investor: "Where Smart Money Meets Island Living"
     - For a family: "Where Weekend Mornings Feel Like Vacation"

2. **hero_subheadline**: One supporting line (max 15 words) with location context.

3. **sections**: Rewrite EACH text section. Keep the factual content but shift the emphasis and tone:
   - Use "you/your" language, making the reader the protagonist
   - Lead with what THEY care about (wellness? ROI? family time?)
   - Be conversational, warm — like a friend who genuinely gets them
   - Keep it concise — no fluff, every sentence earns its place
   - DO NOT start every section with "Imagine" or "Picture this"
   - Include the same key facts (prices, sq ft, amenities list) but frame them through the buyer's lens

4. **curated_usps**: Pick the 4–5 USPs from the list that THIS buyer would care about most. Reword them slightly to feel relevant.

5. **objection_handler_heading** + **objection_handler_content**: What concern would THIS buyer likely have? Address it warmly in 2-3 sentences.
   - Investor worried about ROI? → Reassure with yield data
   - Family worried about safety? → Highlight community features
   - Wellness buyer worried about authenticity? → Emphasize clinical-grade amenities

6. **financial_headline** + **financial_pitch**: Reframe the financial info for this buyer type:
   - Investor → lead with ROI, yield, capital appreciation
   - End-user → lead with "your home from AED X/month" (affordability)
   - HNI → lead with exclusivity, limited availability

7. **cta_text**: A short CTA button label (max 4 words) that resonates with this buyer:
   - Investor → "View Investment Details"
   - Family → "Book a Visit"
   - Wellness → "Explore Wellness Living"

8. **cta_heading**: A CTA section heading personalized for this buyer (max 8 words).

9. **highlighted_amenity_categories**: Pick the 2-3 most relevant amenity categories for this buyer from:
   ["social", "work", "recreation", "family", "wellness", "fitness"]
   - Investor → ["recreation", "social"]
   - Family → ["family", "recreation"]
   - Wellness → ["wellness", "fitness"]

10. **top_amenities**: Pick 4 to 6 amenities from this list that would matter MOST to THIS buyer.
   IMPORTANT: Only pick amenities that have images (marked with ✓ below).
   Available amenities with images: Working Pods ✓, Green House Cafe ✓, Infinity Pool ✓, Pool ✓,
   Kids Pool ✓, Cryotherapy ✓, Red Light Therapy ✓, Hyperbaric Chamber ✓, Gym ✓, Outdoor Gym ✓,
   Aqua Gym ✓, Kids Play Area ✓.
   For each, write a 1-2 sentence description tailored to this persona:
   - Investor → highlight amenities that drive rental premiums and tenant appeal
   - Family → highlight safe, fun, kid-friendly spaces
   - Wellness → highlight recovery, biohacking, and fitness amenities
   - General → highlight unique and premium experiences
   Return as list of objects: [{{"name": "exact amenity name", "description": "tailored text"}}]

11. **ambassador_desc**: Rewrite the brand ambassador description so it resonates with THIS buyer persona.
    - Keep the same approximate length as the original (3-4 sentences).
    - Draw a connection between the ambassador's values/background and what this buyer cares about.
    - Original ambassador description: {ambassador_description}

12. **services_intro**: Write a 1-2 sentence intro for the à la carte services section that speaks to THIS buyer:
    - For a wellness buyer → frame as "your personal wellness concierge"
    - For a family → frame around convenience and childcare peace of mind
    - For an investor/HNI → frame around premium living standards that justify premium rents
    - Available services: {services_list}

## TONE RULES
- Sound like a thoughtful friend, never a brochure
- No exclamation marks overload. One per section max
- Avoid "nestled", "boasts", "unparalleled", "redefine" — these are dead words
- Be specific, not vague. "53 wellness amenities" beats "world-class facilities"
- Write for someone scrolling on their phone — short paragraphs, scannable
"""


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

    # 3. Collect amenities that have images (for nested card generation)
    amenities_with_images = [
        a for a in (prop.get("amenities_grid") or []) if a.get("image_url")
    ]

    # 4. Generate 8-card story via LLM
    story_cards = await _generate_storycard_content(persona, prop, amenities_with_images)

    # 5. Render HTML with enriched content using the new card renderer
    html_content = _render_microsite_card_html(persona, prop, story_cards)

    # 6. Deactivate any existing microsites for this persona, then create new one
    ms_col = get_collection(MICROSITE_COLLECTION)
    await ms_col.update_many(
        {"url_slug": persona_id, "is_active": True},
        {"$set": {"is_active": False}}
    )

    microsite = MicrositeDocument(
        persona_id=persona_id,
        property_id=property_id,
        html_content=html_content,
        url_slug=persona_id,
    )
    await ms_col.insert_one(microsite.model_dump())

    microsite_url = f"{settings.APP_BASE_URL}/m/{microsite.url_slug}"

    return {
        "microsite_url": microsite_url,
        "tracking_id": microsite.tracking_id,
        "microsite_id": microsite.microsite_id,
    }


def _filter_assets(assets: List[Dict], persona: Dict) -> List[Dict]:
    """Filter assets based on persona's lifestyle tags and deal breaker features."""
    lifestyle = persona.get("lifestyle", {})
    key_interests = [k.lower() for k in lifestyle.get("lifestyle_tags", []) + lifestyle.get("must_have_amenities", [])]
    ignored = [i.lower() for i in lifestyle.get("deal_breaker_features", [])]

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

    persona_type = persona.get("ai_recommended_persona_type", "General")
    motivation = persona.get("motivation", {}).get("primary_goal", "")

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


# ── AI Content Enrichment ───────────────────────────────────────

async def _enrich_content(persona: Dict, prop: Dict, assets: List[Dict]) -> Dict[str, Any]:
    """
    Single LLM call to generate all persona-optimized content:
    hero headline, rewritten sections, curated USPs, objection handler, financial pitch.
    """
    # Extract text sections from assets
    text_sections = []
    for asset in assets:
        if asset.get("type") == "text":
            text_sections.append({
                "description": asset.get("description", ""),
                "content": asset.get("content", ""),
            })

    # Build a concise persona summary for the prompt
    persona_summary = {
        "persona_type": persona.get("ai_recommended_persona_type", ""),
        "persona_label": persona.get("ai_persona_label", ""),
        "primary_goal": persona.get("motivation", {}).get("primary_goal", ""),
        "buying_motivation": persona.get("motivation", {}).get("buying_motivation", ""),
        "lifestyle_tags": persona.get("lifestyle", {}).get("lifestyle_tags", []),
        "deal_breaker_features": persona.get("lifestyle", {}).get("deal_breaker_features", []),
        "must_have_amenities": persona.get("lifestyle", {}).get("must_have_amenities", []),
        "budget": persona.get("financial", {}),
        "identity": persona.get("identity", {}),
        "sales_angle": persona.get("ai_recommended_angle", ""),
    }

    # Brand ambassador description for persona-tailored rewrite
    ambassador = prop.get("brand_ambassador", {})
    ambassador_description = ambassador.get("description", "") if ambassador else ""

    # A la carte services list
    services_list = ", ".join(prop.get("a_la_carte_services") or [])

    prompt = ENRICHMENT_PROMPT.format(
        persona_json=json.dumps(persona_summary, indent=2, default=str),
        property_name=prop.get("name", ""),
        property_location=prop.get("location", ""),
        developer=prop.get("developer", ""),
        property_type=prop.get("property_type", ""),
        price_start=prop.get("price_start_aed_in_million", ""),
        price_end=prop.get("price_end_aed_in_million", ""),
        usps=", ".join(prop.get("usps") or []),
        sections_json=json.dumps(text_sections, indent=2),
        ambassador_description=ambassador_description,
        services_list=services_list,
    )

    try:
        result_text = ai_client.structured_completion(
            messages=[
                {"role": "system", "content": "You are a warm, empathetic real estate copywriter. Return valid JSON matching the requested structure."},
                {"role": "user", "content": prompt},
            ],
            response_structure=EnrichedMicrositeContent,
        )
        enriched = json.loads(result_text)
        print(f"✅ AI Enrichment complete: {enriched.get('hero_headline', '')}")
        return enriched

    except Exception as e:
        print(f"⚠️ AI Enrichment failed, using original content: {e}")
        # Graceful fallback — return empty enrichment, template will use originals
        return {
            "hero_headline": "",
            "hero_subheadline": "",
            "sections": [],
            "curated_usps": [],
            "objection_handler_heading": "",
            "objection_handler_content": "",
            "financial_headline": "",
            "financial_pitch": "",
            "cta_text": "Express Interest",
            "cta_heading": "Ready to Explore?",
            "highlighted_amenity_categories": [],
            "top_amenities": [],
            "ambassador_desc": "",
            "services_intro": "",
        }


def _hex_to_rgb(hex_color: str) -> str:
    """Convert hex color to RGB string for CSS rgba() usage."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"
    return "30, 136, 229"  # Default blue


def _get_section_order(persona: Dict, use_clone: bool = False) -> list:
    """Determine content section order based on buyer persona motivation."""
    motivation = persona.get("motivation", {}).get("primary_goal", "").lower()

    if use_clone:
        # Full cloned template section ordering
        if "invest" in motivation or "rental" in motivation:
            return ["hero", "brand_vision", "usp_cards", "financial", "gallery",
                    "location", "amenities", "wellness", "services", "objection", "contact"]
        elif "family" in motivation or "end-use" in motivation or "end_use" in motivation:
            return ["hero", "brand_vision", "amenities", "wellness", "gallery",
                    "services", "usp_cards", "location", "financial", "objection", "contact"]
        elif "wellness" in motivation or "health" in motivation or "biohack" in motivation:
            return ["hero", "brand_vision", "wellness", "amenities", "services",
                    "usp_cards", "gallery", "location", "financial", "objection", "contact"]
        else:
            return ["hero", "brand_vision", "usp_cards", "wellness", "amenities",
                    "gallery", "services", "location", "financial", "objection", "contact"]
    else:
        # Legacy simple template
        if "invest" in motivation or "rental" in motivation:
            return ["roi", "pricing", "overview", "amenities", "golden_visa"]
        elif "family" in motivation or "end-use" in motivation or "end_use" in motivation:
            return ["overview", "amenities", "golden_visa", "pricing", "roi"]
        else:
            return ["overview", "amenities", "pricing", "roi", "golden_visa"]


def _order_items_by_persona(items: List[Dict], persona: Dict, enriched: Dict,
                            name_key: str = 'name', category_key: str = 'category') -> List[Dict]:
    """
    Reorder and highlight items (amenities, USP cards, wellness features)
    based on persona interests and AI-highlighted categories.
    """
    lifestyle = persona.get("lifestyle", {})
    interests = [t.lower() for t in lifestyle.get("lifestyle_tags", []) + lifestyle.get("must_have_amenities", [])]
    motivation = persona.get("motivation", {}).get("primary_goal", "").lower()
    highlighted_cats = [c.lower() for c in enriched.get("highlighted_amenity_categories", [])]

    # Infer highlight categories from motivation if AI didn't provide them
    if not highlighted_cats:
        if "invest" in motivation or "rental" in motivation:
            highlighted_cats = ["recreation", "social"]
        elif "family" in motivation:
            highlighted_cats = ["family", "recreation"]
        elif "wellness" in motivation or "health" in motivation:
            highlighted_cats = ["wellness", "fitness"]
        else:
            highlighted_cats = ["recreation", "wellness"]

    scored = []
    for item in items:
        new_item = dict(item)
        cat = item.get(category_key, "").lower()
        name = item.get(name_key, item.get('title', '')).lower()
        score = 0
        is_highlighted = False

        if cat in highlighted_cats:
            score += 10
            is_highlighted = True
        if any(interest in name or interest in cat for interest in interests):
            score += 5
            is_highlighted = True

        new_item['highlighted'] = is_highlighted
        scored.append((score, new_item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored]


def _render_microsite_card_html(persona: Dict, prop: Dict, story_cards: List[Dict]) -> str:
    """Render the microsite HTML from the V2 storycard template."""
    template_path = Path(__file__).parent.parent / "templates" / "microsite_storycard.html"
    template_str = template_path.read_text() if template_path.exists() else ""
    template = Template(template_str)

    return template.render(
        persona=persona,
        property=prop,
        story_cards=story_cards,
        broker_name=prop.get("broker_name", "Your Broker"),
        broker_phone=prop.get("broker_phone", ""),
        broker_email=prop.get("broker_email", ""),
        broker_logo_url=prop.get("broker_logo_url", ""),
        tracking_id=persona.get("persona_id", ""),
        base_url=settings.APP_BASE_URL,
    )


def _render_microsite_html(persona: Dict, prop: Dict, assets: List[Dict], enriched: Dict = None) -> str:
    """Render the microsite HTML from the appropriate template."""
    enriched = enriched or {}

    # Use clone template if property has the structured data (hero_video_url, usp_cards, etc.)
    use_clone = bool(prop.get("usp_cards") or prop.get("amenities_grid"))

    if use_clone:
        print
        return ""
        template_path = Path(__file__).parent.parent / "templates" / "microsite_clone.html"
    else:
        template_path = Path(__file__).parent.parent / "templates" / "microsite.html"

    if template_path.exists():
        template_str = template_path.read_text()
    else:
        template_str = _get_fallback_template()

    template = Template(template_str)

    brand_color = prop.get("brand_color", "#1a73e8")
    section_order = _get_section_order(persona, use_clone=use_clone)

    # Extract hero image (first image asset)
    hero_image_url = ""
    for asset in assets:
        if asset.get("type") == "image":
            hero_image_url = asset.get("url", "")
            break

    # Build enriched sections lookup for the template
    enriched_sections = {}
    for sec in enriched.get("sections", []):
        enriched_sections[sec.get("section_key", "")] = sec

    # Inject AI-generated services intro as a virtual section
    if enriched.get("services_intro"):
        enriched_sections["a_la_carte_services"] = {
            "section_key": "a_la_carte_services",
            "heading": "On-Demand Hospitality",
            "content": enriched["services_intro"],
        }

    # Resolve brand ambassador description (AI-personalized or fallback to original)
    ambassador = prop.get("brand_ambassador", {})
    ambassador_desc = enriched.get("ambassador_desc") or (ambassador.get("description", "") if ambassador else "")

    # Persona-ordered items for the clone template
    usp_cards_ordered = _order_items_by_persona(
        prop.get("usp_cards", []), persona, enriched,
        name_key='title', category_key='category'
    ) if use_clone else []

    amenities_ordered = _order_items_by_persona(
        prop.get("amenities_grid") or [], persona, enriched,
        name_key='name', category_key='category'
    ) if use_clone else []

    wellness_features_ordered = _order_items_by_persona(
        prop.get("wellness_features", []), persona, enriched,
        name_key='title', category_key='category'
    ) if use_clone else []

    # Determine which services to highlight based on persona
    highlighted_services = _get_highlighted_services(persona) if use_clone else []

    # Build top amenities with images for the showcase carousel
    top_amenities_with_images = []
    if use_clone:
        amenities_lookup = {a.get('name', '').lower(): a for a in prop.get('amenities_grid', [])}
        used_images = set()  # Deduplicate by image URL
        for ai_amenity in enriched.get('top_amenities', []):
            key = ai_amenity.get('name', '').lower()
            match = amenities_lookup.get(key)
            img_url = match.get('image_url', '') if match else ''
            if match and img_url and img_url not in used_images:
                top_amenities_with_images.append({
                    'name': ai_amenity.get('name', ''),
                    'description': ai_amenity.get('description', ''),
                    'image_url': img_url,
                    'category': match.get('category', ''),
                })
                used_images.add(img_url)
        # Fallback: if AI didn't pick enough, fill from amenities that have unique images
        if len(top_amenities_with_images) < 4:
            used_names = {a.get('name', '').lower() for a in top_amenities_with_images}
            for amenity in amenities_ordered:
                if len(top_amenities_with_images) >= 6:
                    break
                img_url = amenity.get('image_url', '')
                if img_url and img_url not in used_images and amenity.get('name', '').lower() not in used_names:
                    top_amenities_with_images.append({
                        'name': amenity.get('name', ''),
                        'description': '',
                        'image_url': img_url,
                        'category': amenity.get('category', ''),
                    })
                    used_names.add(amenity.get('name', '').lower())
                    used_images.add(img_url)

    # Build gallery categories from image assets for tabbed gallery
    gallery_categories = []
    if use_clone:
        # Group images by category
        cat_map = {}
        for asset in assets:
            if asset.get('type') == 'image' and asset.get('category'):
                cat = asset['category']
                if cat not in cat_map:
                    cat_map[cat] = []
                cat_map[cat].append(asset)

        # Persona-driven tab order
        motivation = str(persona.get("motivation", "")).lower()
        if "invest" in motivation or "rental" in motivation:
            preferred_order = ["Interiors", "Amenities", "Views", "Exteriors"]
        elif "family" in motivation or "end" in motivation:
            preferred_order = ["Interiors", "Amenities", "Exteriors", "Views"]
        elif "wellness" in motivation or "health" in motivation:
            preferred_order = ["Amenities", "Interiors", "Views", "Exteriors"]
        else:
            preferred_order = ["Amenities", "Interiors", "Exteriors", "Views"]

        for cat_name in preferred_order:
            if cat_name in cat_map:
                gallery_categories.append({
                    'name': cat_name,
                    'images': cat_map[cat_name],
                })
        # Add any remaining categories not in preferred_order
        for cat_name, imgs in cat_map.items():
            if cat_name not in preferred_order:
                gallery_categories.append({'name': cat_name, 'images': imgs})

    gallery_tab_names = [c['name'] for c in gallery_categories]

    return template.render(
        persona=persona,
        property=prop,
        assets=assets,
        brand_color=brand_color,
        brand_color_rgb=_hex_to_rgb(brand_color),
        persona_section_order=section_order,
        hero_image_url=hero_image_url,
        enriched=enriched,
        enriched_sections=enriched_sections,
        # Clone template extras
        usp_cards_ordered=usp_cards_ordered,
        amenities_ordered=amenities_ordered,
        wellness_features_ordered=wellness_features_ordered,
        highlighted_services=highlighted_services,
        top_amenities_with_images=top_amenities_with_images,
        gallery_categories=gallery_categories,
        gallery_tab_names=gallery_tab_names,
        # New: ambassador + services
        ambassador_desc=ambassador_desc,
        # Common
        broker_name=prop.get("broker_name", "Your Broker"),
        broker_phone=prop.get("broker_phone", ""),
        broker_email=prop.get("broker_email", ""),
        broker_logo_url=prop.get("broker_logo_url", ""),
        tracking_id=persona.get("persona_id", ""),
        base_url=settings.APP_BASE_URL,
    )


def _get_highlighted_services(persona: Dict) -> List[str]:
    """Return à la carte services to highlight based on persona lifestyle."""
    motivation = persona.get("motivation", {}).get("primary_goal", "").lower()
    lifestyle_tags = [t.lower() for t in persona.get("lifestyle", {}).get("lifestyle_tags", [])]

    highlights = []
    if "family" in motivation or "family" in " ".join(lifestyle_tags):
        highlights.extend(["Childcare Assistance", "Grocery And Shopping Assistance", "24-Hour Emergency Repair"])
    if "wellness" in motivation or "health" in " ".join(lifestyle_tags):
        highlights.extend(["In-Home Massage Services", "Health Consultations"])
    if "invest" in motivation or "luxury" in " ".join(lifestyle_tags):
        highlights.extend(["Chauffeur Driven Rolls Royce", "Private Boating With Captain"])
    if not highlights:
        highlights = ["Chauffeur Driven Rolls Royce", "Private Boating With Captain", "In-Home Massage Services"]
    return highlights


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
            {% if persona.get('ai_recommended_angle') %}
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


# ════════════════════════════════════════════════════════════════════════════
# V2 — STORYCARD MICROSITE
# A pure 8-card narrative pitch experience.
# Each card is a beat in a persuasive story arc.
# ════════════════════════════════════════════════════════════════════════════

class NestedCardItem(BaseModel):
    image_url: str = ""
    title: str = ""
    description: str        # 1-2 sentences, persona-tailored

class TableRow(BaseModel):
    label: str
    value: str

class StoryCard(BaseModel):
    card_id: str            # e.g. "card_1_problem"
    step_label: str         # e.g. "1 of 8  •  Observation"
    title: str              # Large heading on the card
    subtitle: str = ""      # Optional sub-heading
    main: str = ""          # Big gold stat / single line
    supporting: str = ""    # Body copy below main
    bullets: List[str] = [] # Optional bullet points (card 5 — differentiators)
    detail_type: str = "simple"  # 'simple' | 'table' | 'nested' | 'none'
    detail_text: str = ""
    table_details: List[TableRow] = []
    nested_cards: List[NestedCardItem] = []

class StorycardContent(BaseModel):
    cards: List[StoryCard]  # Exactly 8 cards


STORYCARD_PROMPT = """You are a world-class property sales strategist and copywriter.
Your task: generate a premium 8-card story pitch that guides THIS specific buyer persona through
a powerful, emotionally resonant narrative arc — from problem recognition to confident action.

## BUYER PERSONA
{persona_json}

## PROPERTY
- Name: {property_name}
- Location: {property_location}
- Developer: {developer}
- Type: {property_type}
- Price: AED {price_start}M - {price_end}M
- USPs: {usps}
- Key amenities available with images: {amenity_image_names}
- A la carte services: {services_list}
- Brand ambassador: {ambassador_name}
- Sales angle for this persona: {sales_angle}

## THE 8-CARD STORY ARC — generate exactly 8 StoryCard objects:

### CARD 1 — Problem Statement (Tension)
- card_id: "card_1_problem"
- step_label: "1 of 8  •  Observation"
- title: A short relatable observation the buyer already agrees with (max 10 words, neutral question or fact)
- supporting: 2 sentences that expand the tension. Make them feel seen.
- main: Leave empty
- detail_type: "simple"
- detail_text: 2-3 sentences deepening the context around this tension

### CARD 2 — Cost of Status Quo (Reality Check)
- card_id: "card_2_cost"
- step_label: "2 of 8  •  The Cost"
- title: 1 headline naming the hidden cost (financial or strategic)
- main: A striking number or stat (e.g., "AED 600K+")
- supporting: 1 sentence contextualizing the stat
- detail_type: "table"
- table_details: 3-4 rows with real comparisons (Rent vs Own monthly, 5-year cost, equity built)

### CARD 3 — The Shift (Reframe)
- card_id: "card_3_shift"
- step_label: "3 of 8  •  A Different Angle"
- title: A simple perspective change (max 8 words, not pushy)
- supporting: 2 sentences opening up a new way to see the situation
- main: Leave empty
- detail_type: "simple"
- detail_text: 2 sentences expanding the reframe

### CARD 4 — Property as the Answer (Fit)
- card_id: "card_4_fit"
- step_label: "4 of 8  •  The Match"
- title: Introduce {property_name} as a resolution, not a product (max 10 words)
- subtitle: Location + developer line
- supporting: 2 sentences showing alignment between buyer situation and this property
- main: Leave empty
- detail_type: "table"
- table_details: 4 key property facts (Price range, Type, Developer, Handover)

### CARD 5 — Key Differentiators (Why This Works)
- card_id: "card_5_why"
- step_label: "5 of 8  •  Why This"
- title: What makes it different — persona-framed (max 8 words)
- bullets: 4-5 short bullet points, each max 8 words, persona-specific differentiators
- detail_type: "nested"
- nested_cards: Pick 4-5 amenities from the amenity image list that matter MOST to this persona.
  Each nested card: image_url (use the real URL from amenity list), title (amenity name), description (1-2 sentences persona-tailored)

### CARD 6 — Proof (Rational Validation)
- card_id: "card_6_proof"
- step_label: "6 of 8  •  The Numbers"
- title: A financial headline framed for this buyer (max 8 words)
- main: The key number (e.g., "~AED 9,400/mo" or "7.2% ROI")
- supporting: 1 line contextualizing why that number makes sense
- detail_type: "table"
- table_details: 4-5 financial facts (monthly cost, price range, ROI estimate, payment plan, golden visa)

### CARD 7 — Reward (Outcome)
- card_id: "card_7_reward"
- step_label: "7 of 8  •  What Changes"
- title: What actually changes for the buyer (max 8 words, emotional closure)
- supporting: 2 sentences painting the picture of their life after this decision. Warm, specific.
- main: Leave empty
- detail_type: "simple"
- detail_text: 2-3 sentences deepening the emotional outcome

### CARD 8 — Call to Action (Next Step)
- card_id: "card_8_cta"
- step_label: "8 of 8  •  Next Step"
- title: Simple low-friction CTA heading (max 8 words)
- supporting: 2 lines describing what happens next. Concrete, no pressure.
- main: Leave empty
- detail_type: "table"
- table_details: 3 rows: what the buyer gets and how long / cost

## TONE RULES
- Sound like a brilliant, empathetic friend who knows the market — not a salesperson
- No exclamation marks more than once across all 8 cards
- Avoid: "nestled", "boasts", "unparalleled", "redefine", "luxury living"
- Be specific. "53 wellness amenities" beats "world-class facilities"
- Each card must feel like a natural progression from the previous — it is a story, not a list
"""


async def _generate_storycard_content(
    persona: Dict, prop: Dict, amenities_with_images: List[Dict]
) -> List[Dict]:
    """Call the LLM to generate the 8-card story arc for this persona x property."""

    persona_summary = {
        "persona_type": persona.get("ai_recommended_persona_type", ""),
        "persona_label": persona.get("ai_persona_label", ""),
        "primary_goal": persona.get("motivation", {}).get("primary_goal", ""),
        "buying_motivation": persona.get("motivation", {}).get("buying_motivation", ""),
        "lifestyle_tags": persona.get("lifestyle", {}).get("lifestyle_tags", []),
        "must_have_amenities": persona.get("lifestyle", {}).get("must_have_amenities", []),
        "budget": persona.get("financial", {}),
        "identity": persona.get("identity", {}),
        "sales_angle": persona.get("ai_recommended_angle", ""),
    }

    ambassador = prop.get("brand_ambassador", {}) or {}
    amenity_image_names = ", ".join(
        f"{a.get('name','')} (url: {a.get('image_url','')})"
        for a in amenities_with_images
        if a.get("image_url")
    )

    prompt = STORYCARD_PROMPT.format(
        persona_json=json.dumps(persona_summary, indent=2, default=str),
        property_name=prop.get("name", ""),
        property_location=prop.get("location", ""),
        developer=prop.get("developer", ""),
        property_type=prop.get("property_type", ""),
        price_start=prop.get("price_start_aed_in_million", ""),
        price_end=prop.get("price_end_aed_in_million", ""),
        usps=", ".join(prop.get("usps") or []),
        amenity_image_names=amenity_image_names,
        services_list=", ".join(prop.get("a_la_carte_services") or []),
        ambassador_name=ambassador.get("name", ""),
        sales_angle=persona.get("ai_recommended_angle", ""),
    )

    try:
        result_text = ai_client.structured_completion(
            messages=[
                {
                    "role": "system",
                    "content": "You are a premium real estate sales strategist. Return valid JSON matching the requested structure exactly.",
                },
                {"role": "user", "content": prompt},
            ],
            response_structure=StorycardContent,
        )
        data = json.loads(result_text)
        cards = data.get("cards", [])
        print(f"Storycard generated: {len(cards)} cards for persona {persona.get('persona_id', '')}")
        return cards
    except Exception as e:
        print(f"Storycard generation failed: {e}")
        return [
            {
                "card_id": "card_1_problem",
                "step_label": "1 of 8  \u2022  Observation",
                "title": "You have built a life here. Is this home truly yours?",
                "supporting": "Many buyers in your position are paying rent with nothing to show for it. There is a better path.",
                "detail_type": "simple",
                "detail_text": "Every year of renting is a year of building someone else's equity. This is a question worth sitting with.",
            },
            {
                "card_id": "card_8_cta",
                "step_label": "8 of 8  \u2022  Next Step",
                "title": "Review a shortlist — 20 minutes, no obligation",
                "supporting": "A private briefing with financials and a curated shortlist. Available this week.",
                "detail_type": "none",
            },
        ]


async def build_storycard_microsite(persona_id: str, property_id: str) -> Dict[str, Any]:
    """
    Build a V2 storycard microsite — pure 8-card narrative pitch experience.
    Returns: { microsite_url, tracking_id, microsite_id }
    Served at /m/s/{persona_id}
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

    # 3. Collect amenities that have images (for nested card generation)
    amenities_with_images = [
        a for a in (prop.get("amenities_grid") or []) if a.get("image_url")
    ]

    # 4. Generate 8-card story via LLM
    story_cards = await _generate_storycard_content(persona, prop, amenities_with_images)

    # 5. Render HTML from template
    template_path = Path(__file__).parent.parent / "templates" / "microsite_storycard.html"
    template_str = template_path.read_text() if template_path.exists() else ""
    template_obj = Template(template_str)

    html_content = template_obj.render(
        persona=persona,
        property=prop,
        story_cards=story_cards,
        broker_name=prop.get("broker_name", "Your Broker"),
        broker_phone=prop.get("broker_phone", ""),
        broker_email=prop.get("broker_email", ""),
        broker_logo_url=prop.get("broker_logo_url", ""),
        tracking_id=persona.get("persona_id", ""),
        base_url=settings.APP_BASE_URL,
    )

    # 6. Deactivate old storycard microsites for this persona, then persist
    ms_col = get_collection(MICROSITE_COLLECTION)
    storycard_slug = f"s/{persona_id}"
    await ms_col.update_many(
        {"url_slug": storycard_slug, "is_active": True},
        {"$set": {"is_active": False}},
    )

    microsite = MicrositeDocument(
        persona_id=persona_id,
        property_id=property_id,
        html_content=html_content,
        url_slug=storycard_slug,
    )
    await ms_col.insert_one(microsite.model_dump())

    microsite_url = f"{settings.APP_BASE_URL}/m/{storycard_slug}"
    return {
        "microsite_url": microsite_url,
        "tracking_id": microsite.tracking_id,
        "microsite_id": microsite.microsite_id,
    }
