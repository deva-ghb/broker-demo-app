"""
Engagement Tracker API router.
"""
from fastapi import APIRouter, HTTPException

from schemas.engagement_schemas import EngagementBatchRequest, EngagementSummary
from services.engagement_service import ingest_events, get_engagement_summary
from services.trigger_service import evaluate_triggers

router = APIRouter(prefix="/api/v1/engagement", tags=["Engagement Tracker"])


@router.post("/events")
async def receive_events(request: EngagementBatchRequest):
    """
    Receive a batch of engagement events from the client-side tracker.
    Triggers engagement signal aggregation and trigger evaluation.
    """
    await ingest_events(
        tracking_id=request.tracking_id,
        events=[e.model_dump() for e in request.events],
        session_id=request.session_id,
    )

    # Evaluate triggers after ingesting events
    # (resolve persona_id from tracking_id)
    from services.engagement_service import _resolve_persona_id
    persona_id = await _resolve_persona_id(request.tracking_id)
    if persona_id:
        await evaluate_triggers(persona_id)

    return {"status": "ok", "events_received": len(request.events)}


@router.get("/{tracking_id}/summary", response_model=EngagementSummary)
async def engagement_summary(tracking_id: str):
    """Get aggregated engagement summary for a tracking/persona ID."""
    summary = await get_engagement_summary(tracking_id)
    return EngagementSummary(**summary)
