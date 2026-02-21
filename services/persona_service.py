"""
Persona Builder service — AI-driven conversational lead profiling.

Manages guided Q&A sessions with brokers via text and audio,
synthesizing conversations into structured Persona JSON.
"""
import json
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from services.ai_client import ai_client
from services.database import get_collection
from services.knowledge_base import get_property_context, build_property_context_prompt
from models.persona import PersonaDocument, PERSONA_COLLECTION

# In-memory session store: session_id → { messages, partial_persona, property_id, broker_id }
_sessions: Dict[str, Dict] = {}

SYSTEM_PROMPT = """You are SellSmart's Persona Builder — an intelligent real estate sales assistant.
Your job is to have a natural conversation with a broker to understand their client (buyer/investor).

**Your Goals:**
1. Ask adaptive, contextual questions to build a complete buyer persona.
2. Use the property context provided to ask relevant questions.
3. Cover these key areas:
   - Buyer nationality, residency status, language preference
   - Primary motivation (investment, end-use, Golden Visa, etc.)
   - Key interests (ROI, payment plans, developer track record, location, amenities, etc.)
   - Features they DON'T care about (to filter out)
   - Budget range and timeline
   - Trust level / how warm is the lead

**Conversation Style:**
- Be conversational, professional, and concise.
- Ask ONE question at a time (max two if closely related).
- Acknowledge what the broker tells you before asking the next question.
- If the broker provides rich info in one message, extract multiple data points.

**Completion:**
- After gathering enough information (typically 4-8 exchanges), summarize what you've learned and ask if there's anything else.
- When the broker confirms they're done (or says "done", "that's all", "generate", etc.), respond with EXACTLY the marker: [PERSONA_COMPLETE]
- Do NOT include [PERSONA_COMPLETE] until the broker explicitly signals completion or you've covered all key areas and confirmed.

{property_context}
"""

SYNTHESIS_PROMPT = """Based on the following conversation between a broker and the SellSmart system, 
extract a structured buyer persona. Be thorough and infer reasonable values from context.

Conversation:
{conversation}

Generate a JSON object with these exact fields:
{{
    "persona_type": "Investor" | "End-User" | "Family" | "Corporate" | "Other",
    "demographic_context": {{
        "nationality": "...",
        "language_preference": "...",
        "residency_status": "International" | "Local" | "Expat"
    }},
    "primary_motivation": "...",
    "key_interests": ["..."],
    "ignored_features": ["..."],
    "ai_recommended_angle": "A specific sales angle recommendation for the broker",
    "trust_level_score": 0-100,
    "next_best_action": "Specific next step recommendation"
}}

Return ONLY valid JSON, no markdown fences."""


def _get_or_create_session(session_id: Optional[str], broker_id: Optional[str] = None,
                           property_id: Optional[str] = None) -> Tuple[str, Dict]:
    """Get existing session or create a new one."""
    if session_id and session_id in _sessions:
        return session_id, _sessions[session_id]

    new_id = session_id or f"sess_{uuid.uuid4().hex[:8]}"
    _sessions[new_id] = {
        "messages": [],
        "broker_id": broker_id,
        "property_id": property_id,
        "status": "collecting",
        "persona_id": None,
    }
    return new_id, _sessions[new_id]


async def handle_text_chat(
    message: str,
    session_id: Optional[str] = None,
    broker_id: Optional[str] = None,
    property_id: Optional[str] = None,
) -> Dict:
    """
    Handle a text message in the persona building conversation.
    Returns: { session_id, reply, session_status, persona_id? }
    """
    session_id, session = _get_or_create_session(session_id, broker_id, property_id)

    # Build system prompt with property context if available
    property_context = ""
    if session.get("property_id"):
        prop_data = await get_property_context(session["property_id"])
        property_context = build_property_context_prompt(prop_data)

    system_msg = SYSTEM_PROMPT.format(
        property_context=f"\n**Property Context:**\n{property_context}" if property_context else ""
    )

    # Add user message to history
    session["messages"].append({"role": "user", "content": message})

    # Build full message list for AI
    ai_messages = [{"role": "system", "content": system_msg}] + session["messages"]

    # Get AI response
    reply, _, _ = ai_client.completion(ai_messages)

    # Check if persona is complete
    if "[PERSONA_COMPLETE]" in reply:
        reply = reply.replace("[PERSONA_COMPLETE]", "").strip()
        session["status"] = "complete"

        # Synthesize persona
        persona_id = await _synthesize_persona(session)
        session["persona_id"] = persona_id

        return {
            "session_id": session_id,
            "reply": reply,
            "session_status": "complete",
            "persona_id": persona_id,
        }

    # Add AI response to history
    session["messages"].append({"role": "assistant", "content": reply})

    return {
        "session_id": session_id,
        "reply": reply,
        "session_status": "collecting",
        "persona_id": None,
    }


async def _synthesize_persona(session: Dict) -> str:
    """
    Synthesize the conversation into a structured Persona JSON and persist it.
    """
    # Format conversation for synthesis
    conversation_text = "\n".join(
        f"{'Broker' if m['role'] == 'user' else 'AI'}: {m['content']}"
        for m in session["messages"]
    )

    synthesis_messages = [
        {"role": "system", "content": "You are a data extraction assistant. Extract structured persona data from conversations."},
        {"role": "user", "content": SYNTHESIS_PROMPT.format(conversation=conversation_text)},
    ]

    result, _, _ = ai_client.completion(synthesis_messages)

    # Parse the JSON
    try:
        persona_data = json.loads(result)
    except json.JSONDecodeError:
        # Try to extract JSON from the response
        import re
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            persona_data = json.loads(json_match.group())
        else:
            persona_data = {}

    # Create persona document
    persona = PersonaDocument(
        broker_id=session.get("broker_id"),
        persona_type=persona_data.get("persona_type"),
        demographic_context=persona_data.get("demographic_context", {}),
        primary_motivation=persona_data.get("primary_motivation"),
        key_interests=persona_data.get("key_interests", []),
        ignored_features=persona_data.get("ignored_features", []),
        ai_recommended_angle=persona_data.get("ai_recommended_angle"),
        trust_level_score=persona_data.get("trust_level_score", 50),
        next_best_action=persona_data.get("next_best_action"),
        conversation_history=session["messages"],
        session_status="complete",
    )

    # Persist to MongoDB
    collection = get_collection(PERSONA_COLLECTION)
    await collection.insert_one(persona.model_dump())

    return persona.persona_id


async def get_persona(persona_id: str) -> Optional[Dict]:
    """Retrieve a persona by ID."""
    collection = get_collection(PERSONA_COLLECTION)
    doc = await collection.find_one({"persona_id": persona_id})
    if doc:
        doc.pop("_id", None)
    return doc


async def list_personas(broker_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """List personas, optionally filtered by broker."""
    collection = get_collection(PERSONA_COLLECTION)
    query = {"broker_id": broker_id} if broker_id else {}
    cursor = collection.find(query).sort("created_at", -1).limit(limit)
    results = []
    async for doc in cursor:
        doc.pop("_id", None)
        results.append(doc)
    return results
