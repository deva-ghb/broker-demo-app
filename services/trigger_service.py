"""
Trigger Mechanism service — evaluates engagement metrics against intent thresholds
and generates actionable broker alerts.
"""
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from services.database import get_collection
from services.ai_client import ai_client
from models.persona import PERSONA_COLLECTION
from models.engagement import ENGAGEMENT_COLLECTION
from models.trigger import TriggerDocument, TRIGGER_COLLECTION

# ─── Configurable Thresholds ─────────────────────────

HIGH_INTENT_VISIT_THRESHOLD = 3          # ≥ 3 page opens
HIGH_INTENT_RETURN_HOURS = 24            # Return within 24 hours
SPECIFIC_INTEREST_DWELL_SECONDS = 120    # 2+ minutes on a section
COMPLETION_SCROLL_THRESHOLD = 100        # 100% scroll depth


async def evaluate_triggers(persona_id: str) -> List[Dict[str, Any]]:
    """
    Evaluate engagement data against intent thresholds and generate triggers.
    Returns list of new triggers created.
    """
    persona_col = get_collection(PERSONA_COLLECTION)
    persona = await persona_col.find_one({"persona_id": persona_id})
    if not persona:
        return []

    persona.pop("_id", None)
    signals = persona.get("engagement_signals", {})
    new_triggers = []

    # ─── Rule 1: High Intent Signal ──────────────────
    page_views = signals.get("total_page_views", 0)
    return_visits = signals.get("return_visit_count", 0)

    if page_views >= HIGH_INTENT_VISIT_THRESHOLD or return_visits >= 1:
        trigger = await _create_trigger(
            persona_id=persona_id,
            trigger_type="high_intent",
            message=f"🔥 Hot Lead — {page_views} views, {return_visits} return visits. Immediate follow-up recommended.",
            confidence=min(0.95, 0.6 + (page_views * 0.05) + (return_visits * 0.1)),
            timing="Call Now",
            persona=persona,
            context=f"Opened the microsite {page_views} times with {return_visits} return visits.",
        )
        if trigger:
            new_triggers.append(trigger)

    # ─── Rule 2: Specific Interest Signal ────────────
    dwell_times = signals.get("section_dwell_times", {})
    for section, dwell in dwell_times.items():
        if dwell >= SPECIFIC_INTEREST_DWELL_SECONDS:
            section_name = section.replace("_", " ").title()
            trigger = await _create_trigger(
                persona_id=persona_id,
                trigger_type="specific_interest",
                message=f"📊 High interest in '{section_name}' — {round(dwell / 60, 1)} minutes of focused viewing.",
                confidence=min(0.9, 0.5 + (dwell / 300)),
                timing="Call Now" if dwell >= 240 else "Wait 2 Hours",
                persona=persona,
                context=f"Spent {round(dwell, 1)} seconds on the '{section_name}' section.",
            )
            if trigger:
                new_triggers.append(trigger)

    # ─── Rule 3: Completion Signal ───────────────────
    max_scroll = signals.get("max_scroll_depth", 0)
    eng_col = get_collection(ENGAGEMENT_COLLECTION)
    cta_clicks = await eng_col.count_documents({
        "persona_id": persona_id,
        "event_type": "cta_click",
    })

    if max_scroll >= COMPLETION_SCROLL_THRESHOLD or cta_clicks > 0:
        message = "✅ They've reviewed everything."
        if cta_clicks > 0:
            message += f" Clicked the CTA {cta_clicks} time(s) but hasn't converted yet."
        message += " Close the loop now."

        trigger = await _create_trigger(
            persona_id=persona_id,
            trigger_type="completion",
            message=message,
            confidence=0.85 if cta_clicks > 0 else 0.7,
            timing="Call Now",
            persona=persona,
            context=f"Scrolled to {max_scroll}% with {cta_clicks} CTA clicks.",
        )
        if trigger:
            new_triggers.append(trigger)

    return new_triggers


async def _create_trigger(
    persona_id: str,
    trigger_type: str,
    message: str,
    confidence: float,
    timing: str,
    persona: Dict,
    context: str,
) -> Optional[Dict]:
    """
    Create a trigger if one of the same type doesn't already exist (avoid duplicates).
    Uses AI to generate a specific talking point.
    """
    trig_col = get_collection(TRIGGER_COLLECTION)

    # Check for existing active trigger of same type
    existing = await trig_col.find_one({
        "persona_id": persona_id,
        "trigger_type": trigger_type,
        "is_active": True,
    })
    if existing:
        return None  # Don't create duplicates

    # Generate AI talking point
    talking_point = await _generate_talking_point(persona, context)

    trigger = TriggerDocument(
        persona_id=persona_id,
        trigger_type=trigger_type,
        message=message,
        confidence_score=round(confidence, 2),
        timing=timing,
        talking_point=talking_point,
    )

    await trig_col.insert_one(trigger.model_dump())

    return trigger.model_dump()


async def _generate_talking_point(persona: Dict, context: str) -> str:
    """Use AI to generate a specific talking point for the broker."""
    try:
        prompt = f"""You are a real estate sales coach. Based on this buyer persona and engagement data,
generate ONE specific, actionable talking point for the broker's next call.

Buyer Profile:
- Type: {persona.get('persona_type', 'Unknown')}
- Motivation: {persona.get('primary_motivation', 'Unknown')}
- Key Interests: {', '.join(persona.get('key_interests', []))}
- Engagement: {context}

Previous AI Recommendation: {persona.get('ai_recommended_angle', 'None')}

Return ONLY the talking point as a single concise sentence (max 25 words). No quotes or formatting."""

        result, _, _ = ai_client.completion(
            [{"role": "user", "content": prompt}]
        )
        return result.strip()
    except Exception:
        return f"Discuss {persona.get('primary_motivation', 'their interests')} based on recent engagement."


async def get_active_triggers(persona_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """Get active triggers, optionally filtered by persona/lead."""
    trig_col = get_collection(TRIGGER_COLLECTION)
    query = {"is_active": True}
    if persona_id:
        query["persona_id"] = persona_id

    cursor = trig_col.find(query).sort("created_at", -1).limit(limit)
    results = []
    async for doc in cursor:
        doc.pop("_id", None)
        results.append(doc)
    return results


async def mark_trigger_read(trigger_id: str):
    """Mark a trigger as read."""
    trig_col = get_collection(TRIGGER_COLLECTION)
    await trig_col.update_one(
        {"trigger_id": trigger_id},
        {"$set": {"is_read": True}},
    )
