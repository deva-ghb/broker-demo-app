"""
Trigger Mechanism API router.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import asyncio
import json

from schemas.trigger_schemas import TriggerResponse, TriggerListResponse
from services.trigger_service import get_active_triggers, evaluate_triggers, mark_trigger_read

router = APIRouter(prefix="/api/v1/triggers", tags=["Trigger Mechanism"])


@router.get("/get", response_model=TriggerListResponse)
async def get_triggers(lead_id: Optional[str] = Query(None, description="Persona/lead ID to filter by")):
    """
    Fetch active, prioritized triggers for a specific lead or the broker's entire pipeline.
    """
    triggers = await get_active_triggers(persona_id=lead_id)
    return TriggerListResponse(
        triggers=[TriggerResponse(**t) for t in triggers],
        total=len(triggers),
    )


@router.post("/evaluate/{persona_id}")
async def evaluate_persona_triggers(persona_id: str):
    """Manually trigger evaluation for a specific persona."""
    new_triggers = await evaluate_triggers(persona_id)
    return {
        "persona_id": persona_id,
        "new_triggers": len(new_triggers),
        "triggers": new_triggers,
    }


@router.post("/{trigger_id}/read")
async def mark_read(trigger_id: str):
    """Mark a trigger as read by the broker."""
    await mark_trigger_read(trigger_id)
    return {"status": "ok", "trigger_id": trigger_id}


@router.websocket("/stream")
async def trigger_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time trigger push notifications.
    The broker's frontend connects here to receive live alerts.
    """
    await websocket.accept()

    try:
        # Send initial set of active triggers
        triggers = await get_active_triggers()
        await websocket.send_json({
            "type": "initial",
            "triggers": triggers,
        })

        # Poll for new triggers every 10 seconds
        last_count = len(triggers)
        while True:
            await asyncio.sleep(10)
            current_triggers = await get_active_triggers()
            current_count = len(current_triggers)

            if current_count > last_count:
                # New triggers detected — send only the new ones
                new_ones = current_triggers[:current_count - last_count]
                await websocket.send_json({
                    "type": "new_triggers",
                    "triggers": new_ones,
                })

            last_count = current_count

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except Exception:
            pass
