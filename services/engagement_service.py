"""
Engagement Tracker service — ingests, stores, and aggregates engagement events.
Updates persona engagement_signals from tracked data.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from services.database import get_collection
from models.engagement import EngagementEvent, ENGAGEMENT_COLLECTION
from models.persona import PERSONA_COLLECTION
from models.microsite import MICROSITE_COLLECTION


async def ingest_events(tracking_id: str, events: List[Dict], session_id: Optional[str] = None):
    """
    Ingest a batch of engagement events.
    Persists to MongoDB and triggers persona signal updates.
    """
    collection = get_collection(ENGAGEMENT_COLLECTION)

    # Resolve persona_id from tracking_id via microsite
    persona_id = await _resolve_persona_id(tracking_id)

    docs = []
    for event_data in events:
        event = EngagementEvent(
            tracking_id=tracking_id,
            persona_id=persona_id,
            session_id=session_id,
            event_type=event_data.get("event_type", "unknown"),
            payload=event_data.get("payload", {}),
            timestamp=datetime.fromisoformat(event_data["timestamp"]) if event_data.get("timestamp") else datetime.utcnow(),
        )
        docs.append(event.model_dump())

    if docs:
        await collection.insert_many(docs)

    # Update persona engagement signals
    if persona_id:
        await _update_engagement_signals(persona_id, tracking_id)


async def _resolve_persona_id(tracking_id: str) -> Optional[str]:
    """Look up persona_id from the microsite's tracking_id or url_slug."""
    ms_col = get_collection(MICROSITE_COLLECTION)
    # tracking_id might be the persona_id (used as url_slug)
    doc = await ms_col.find_one({
        "$or": [
            {"tracking_id": tracking_id},
            {"url_slug": tracking_id},
        ]
    })
    if doc:
        return doc.get("persona_id")
    return tracking_id  # Fallback: assume tracking_id is persona_id


async def _update_engagement_signals(persona_id: str, tracking_id: str):
    """
    Aggregate engagement events and update the persona's engagement_signals.
    """
    eng_col = get_collection(ENGAGEMENT_COLLECTION)
    persona_col = get_collection(PERSONA_COLLECTION)

    # Count page views
    page_views = await eng_col.count_documents({
        "persona_id": persona_id,
        "event_type": "page_view",
    })

    # Count unique sessions (return visits)
    pipeline = [
        {"$match": {"persona_id": persona_id, "event_type": "page_view"}},
        {"$group": {"_id": "$session_id"}},
        {"$count": "unique_sessions"},
    ]
    sessions_result = await eng_col.aggregate(pipeline).to_list(1)
    unique_sessions = sessions_result[0]["unique_sessions"] if sessions_result else 1

    # Aggregate section dwell times
    dwell_pipeline = [
        {"$match": {"persona_id": persona_id, "event_type": "section_focus"}},
        {"$group": {
            "_id": "$payload.section",
            "total_dwell": {"$sum": "$payload.dwell_seconds"},
        }},
    ]
    dwell_results = await eng_col.aggregate(dwell_pipeline).to_list(100)
    section_dwell_times = {}
    high_dwell_sections = []
    for d in dwell_results:
        section = d["_id"]
        dwell = d["total_dwell"]
        section_dwell_times[section] = round(dwell, 1)
        if dwell >= 60:  # > 1 minute = high dwell
            high_dwell_sections.append(section)

    # Max scroll depth
    scroll_pipeline = [
        {"$match": {"persona_id": persona_id, "event_type": "scroll_depth"}},
        {"$group": {"_id": None, "max_depth": {"$max": "$payload.depth_percent"}}},
    ]
    scroll_result = await eng_col.aggregate(scroll_pipeline).to_list(1)
    max_scroll = scroll_result[0]["max_depth"] if scroll_result else 0

    # CTA clicks count
    cta_clicks = await eng_col.count_documents({
        "persona_id": persona_id,
        "event_type": "cta_click",
    })

    # Last active
    last_event = await eng_col.find_one(
        {"persona_id": persona_id},
        sort=[("timestamp", -1)],
    )
    last_active = last_event["timestamp"] if last_event else None

    # Update persona document
    await persona_col.update_one(
        {"persona_id": persona_id},
        {"$set": {
            "engagement_signals.total_page_views": page_views,
            "engagement_signals.return_visit_count": max(0, unique_sessions - 1),
            "engagement_signals.section_dwell_times": section_dwell_times,
            "engagement_signals.high_dwell_sections": high_dwell_sections,
            "engagement_signals.max_scroll_depth": max_scroll,
            "engagement_signals.last_active_timestamp": last_active,
            "updated_at": datetime.utcnow(),
        }},
    )


async def get_engagement_summary(tracking_id: str) -> Dict[str, Any]:
    """Get aggregated engagement summary for a tracking ID."""
    persona_id = await _resolve_persona_id(tracking_id)

    eng_col = get_collection(ENGAGEMENT_COLLECTION)

    page_views = await eng_col.count_documents({"persona_id": persona_id, "event_type": "page_view"})

    # Unique sessions
    pipeline = [
        {"$match": {"persona_id": persona_id, "event_type": "page_view"}},
        {"$group": {"_id": "$session_id"}},
        {"$count": "count"},
    ]
    sessions = await eng_col.aggregate(pipeline).to_list(1)
    unique_sessions = sessions[0]["count"] if sessions else 0

    # Section dwell times
    dwell_pipeline = [
        {"$match": {"persona_id": persona_id, "event_type": "section_focus"}},
        {"$group": {"_id": "$payload.section", "total": {"$sum": "$payload.dwell_seconds"}}},
    ]
    dwell_results = await eng_col.aggregate(dwell_pipeline).to_list(100)
    section_dwell = {d["_id"]: round(d["total"], 1) for d in dwell_results}
    high_dwell = [k for k, v in section_dwell.items() if v >= 60]

    # Scroll depth
    scroll_pipeline = [
        {"$match": {"persona_id": persona_id, "event_type": "scroll_depth"}},
        {"$group": {"_id": None, "max": {"$max": "$payload.depth_percent"}}},
    ]
    scroll = await eng_col.aggregate(scroll_pipeline).to_list(1)
    max_scroll = scroll[0]["max"] if scroll else 0

    cta_clicks = await eng_col.count_documents({"persona_id": persona_id, "event_type": "cta_click"})

    last = await eng_col.find_one({"persona_id": persona_id}, sort=[("timestamp", -1)])

    return {
        "tracking_id": tracking_id,
        "persona_id": persona_id,
        "total_page_views": page_views,
        "return_visit_count": max(0, unique_sessions - 1),
        "max_scroll_depth": max_scroll,
        "section_dwell_times": section_dwell,
        "high_dwell_sections": high_dwell,
        "cta_clicks": cta_clicks,
        "last_active": last["timestamp"] if last else None,
    }
