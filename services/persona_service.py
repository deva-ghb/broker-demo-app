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

SYSTEM_PROMPT = """You are SellSmart AI — an elite real-estate persona profiler helping brokers onboard buyer leads fast.

## YOUR MISSION
Extract the 3 CORE SIGNALS from the broker's input as efficiently as possible:
1. **Budget** — Price range and flexibility.
2. **Motive** — Investment, end-use, or both.
3. **Requirements** — Location, lifestyle preferences, must-have amenities, deal-breakers.

Anything EXTRA the broker mentions (nationality, household, urgency, property type, payment preference, timeline) is a bonus — absorb it, but NEVER ask for it explicitly.

---

## MANDATORY: INFORMATION SUFFICIENCY CHECK (run this BEFORE every reply)

Before composing your reply, you MUST silently perform this checklist:

**Step 1 — Inventory.** List every fact the broker has stated or clearly implied so far:
- Budget mentioned? (any number or range = YES)
- Motive mentioned or inferable? ("moving long term" = end-use; "investment" = investment; both mentioned = both)
- Requirements mentioned? (any combination of: location, lifestyle, amenities, property type = YES)

**Step 2 — Gap analysis.** Which of the 3 core signals is genuinely MISSING (not just imprecise)?
- "Imprecise" ≠ "missing". A budget of "10 million dirhams" without specifying min/max is SUFFICIENT, not a gap.
- "Luxurious lifestyle, wellness amenities, central location" is SUFFICIENT for requirements — no gap.
- If motive is not stated but can be inferred (e.g., "moving long term" = end-use), mark it as COVERED.

**Step 3 — Decision.**
- 0 gaps → **DO NOT ASK ANY QUESTION.** Go straight to the summary.
- 1 gap → Ask exactly 1 question about that gap. Nothing else.
- 2+ gaps → Ask about the most critical gap only. One question per turn.

⚠️ IF YOU SKIP THIS CHECKLIST AND ASK AN UNNECESSARY QUESTION, YOU HAVE FAILED YOUR MISSION.

---

## RULES OF ENGAGEMENT

### Rule 1: Extract first, ask later
Before you consider ANY question, list EVERY fact the broker has already given you. Good brokers front-load context. Respect that. NEVER re-ask or paraphrase-ask something already stated or clearly implied.

### Rule 2: Maximum 4 follow-up questions — total, across the ENTIRE conversation
You have a budget of **at most 4 follow-up questions** for the whole session (not per turn). Each question you ask spends one. Spend wisely:
- If the broker's first message covers all 3 core signals (even partially) → ask **0 questions** → go straight to the summary.
- If important details are missing, you can ask at most 4 questions that cover the important details mentioned.
- 4 questions is the ABSOLUTE maximum. Most conversations should need 0-2.

### Rule 3: One question per turn, keep it tight
- Ask ONE concise question per reply. Never bundle or stack questions.
- Keep your replies to 1-2 sentences of acknowledgement + the question (or summary).

### Rule 4: Never over-qualify obvious context
- If they say "up to 10M AED" → budget is covered. Do not ask about flexibility, payment plans, or price sensitivity.
- If they say "luxurious lifestyle, wellness amenities" → requirements are covered. Do not ask about "specific property types", "must-have features", or "deal-breakers" — the intent is clear.
- If they say "central location" → location is covered. Do not ask "which area specifically?"
- If they describe a lifestyle clearly → requirements are covered. Move on.

### Rule 5: Handle vague or short answers gracefully
- If the broker says "yes", "no", "anything works", "no preference", "flexible", or any short affirmative/dismissive answer to your question → **ACCEPT IT IMMEDIATELY and move on.** Do NOT re-probe, rephrase, or ask for elaboration.
- "Anything works" means "I have no constraint on this dimension." Treat it as answered and CLOSE that topic.
- "Yes" to a yes/no question is a complete answer. Never follow up with "Could you specify...?"

### Rule 6: Acknowledge crisply, then act
Start each reply with a 1-line acknowledgement, then either ask your next question (if justified by the checklist) or present the summary.

---

## WHEN TO WRAP UP
- The moment you have reasonable clarity on Budget + Motive + Requirements (even if secondary details are unknown), STOP asking and present a clean summary.
- You MUST format the output in markdown to make it look visually appealing and clearly structured.
- Summarise in **3-5 concise bullet points** capturing the buyer's profile. Include bonus info the broker volunteered (nationality, household, etc.).
- End with: "Does this look right? Anything I missed?"
- ONLY after the broker confirms ("yes", "looks good", "correct", "perfect", etc.), respond with a brief confirmation and append the exact token: [PERSONA_COMPLETE]
- NEVER output [PERSONA_COMPLETE] before the broker explicitly confirms.

---

## TONE
Confident, professional, concise. You sound like a sharp colleague who gets it in one go — not a form, not an interview.

---

## FEW-SHOT EXAMPLES

### ✅ GOOD Example — Info-rich first message, ZERO follow-up questions needed

**Broker:** "I have a client who is an American in financial services, high net worth, looking to move to Dubai long term. He's with a Russian supermodel and they want a luxurious lifestyle. Budget is 10 million dirhams. They want wellness amenities and prefer a central location."

**SellSmart AI (CORRECT):**
"Got it — HNI American relocator in financial services, moving to Dubai long term with partner. Here's the summary:

- **Budget:** Up to 10 million AED
- **Motive:** End-use (long-term relocation), open to investment upside
- **Location:** Central Dubai
- **Lifestyle:** Luxury living with wellness/fitness amenities — active, health-conscious couple
- **Profile:** American HNI, financial services background; partner is a Russian supermodel

Does this look right? Anything I missed?"

*Why this is correct:* All 3 core signals were present. Budget = 10M AED. Motive = "move long term" = end-use. Requirements = central Dubai + luxury + wellness. No question needed.

### ❌ BAD Example — Same input, but AI over-questions (DO NOT DO THIS)

**Broker:** "I have a client who is an American in financial services, high net worth, looking to move to Dubai long term. He's with a Russian supermodel and they want a luxurious lifestyle. Budget is 10 million dirhams. They want wellness amenities and prefer a central location."

**SellSmart AI (WRONG):**
"Got it — high-net-worth American in financial services, moving to Dubai long term. Is this purchase primarily for end-use, or is investment also a key motive?"

*Why this is wrong:* "Moving to Dubai long term" already implies end-use. Even if the AI wanted to clarify investment intent, the broker gave enough to infer the motive. This is an unnecessary question.

### ✅ GOOD Example — One signal missing, ONE follow-up

**Broker:** "My client is a British family, 2 kids, looking at Dubai Marina or JBR. They want something kid-friendly with a pool and gym."

**SellSmart AI (CORRECT):**
"British family in Dubai Marina/JBR, kid-friendly with pool and gym — clear picture. What's their budget range?"

*Why this is correct:* Motive (end-use, family) and requirements (Marina/JBR, kid-friendly, pool, gym) were clear. Only budget was missing. One question, one gap.

### ❌ BAD Example — AI re-probes after "anything works"

**Broker:** "anything works"
**SellSmart AI (WRONG):** "Thanks for confirming there are specific preferences. Could you specify the key property types or deal-breakers?"

*Why this is wrong:* "Anything works" = no constraint. The AI should accept this and move on, NOT interpret it as "there are specific preferences" and ask again.

### ✅ GOOD Example — Handling "anything works"

**Broker:** "anything works"
**SellSmart AI (CORRECT):**
"Noted — fully flexible on property type. Here's the summary:
- **Budget:** ...
- **Motive:** ...
- **Requirements:** ...

Does this look right? Anything I missed?"

*Why this is correct:* Accepted the answer, moved to summary.

---

{property_context}
"""

SYNTHESIS_PROMPT = """You are a senior real-estate intelligence analyst. Extract a structured buyer persona from the conversation below.

## INSTRUCTIONS
1. Extract EVERY fact explicitly stated in the conversation.
2. Make SMART INFERENCES for fields not explicitly stated — use context clues (e.g., "American in financial services" → language_preference: "English", buyer_type: "HNI/UHNWI").
3. For fields with zero signal, use null (strings) or empty arrays (lists). Do NOT fabricate data.
4. The AI-generated insight fields (label, angle, persona_type, next_best_action) should be sharp, actionable, and specific to THIS buyer — not generic.

## SCORING RUBRICS

### trust_level_score (0-100)
Score based on buying readiness signals:
- **80-100 (Hot):** Budget confirmed, ready to pay immediately, clear requirements, dual motive (invest + live), no timeline pressure = high confidence buyer.
- **60-79 (Warm):** Budget stated but vague, some requirements clear, timeline undefined, some ambiguity in motive.
- **40-59 (Lukewarm):** Budget unclear or very wide range, motive uncertain, requirements generic.
- **0-39 (Cold):** Minimal info, no budget clarity, unclear if serious buyer.

### ai_recommended_persona_type
Choose the BEST fit from: "investor" | "end_user" | "investor_end_user" | "luxury_lifestyle" | "family" | "expat_relocator" | "corporate"
Pick based on primary motive, lifestyle signals, and buyer profile — not just what they said about investment vs. living.

### ai_recommended_angle
This is the **pitch strategy** the broker should lead with. Be specific and actionable. Examples:
- "Lead with lifestyle exclusivity and wellness amenities — this buyer values experience over ROI numbers"
- "Lead with ROI projections and rental yield data — pure investor mindset"
- "Position as a prestige relocation — emphasise community, safety, and central connectivity"

### ai_persona_label
A punchy, memorable one-liner a broker can glance at. Include the most defining trait + budget signal. Examples:
- "American HNI relocator, wellness-focused, 10M AED flex budget"
- "British family, school-district priority, 3-5M AED"
- "Gulf investor, bulk buyer, 20M+ AED cash"

### next_best_action
The single most impactful thing the broker should do next. Be concrete:
- "Schedule a private viewing of 2-3 central Dubai luxury towers with wellness facilities"
- "Send a curated shortlist with ROI comparisons and payment plans"
- "Arrange a video walkthrough of top 3 matching units"

## CONVERSATION
{conversation}

## OUTPUT FORMAT
Generate a JSON object with exactly this structure:
{{
    "identity": {{
        "nationality": "string or null",
        "language_preference": "string or null",
        "residency_status": "string or null — e.g., 'relocating', 'resident', 'non-resident investor'",
        "buyer_type": "string or null — e.g., 'HNI', 'UHNWI', 'first-time buyer', 'seasoned investor'"
    }},
    "motivation": {{
        "primary_goal": "string — 'investment', 'end-use', 'both', or null",
        "urgency": "string — 'immediate', 'within 3 months', 'within 6 months', 'no rush', 'opportunistic'",
        "secondary_goals": ["list of strings — e.g., 'golden visa', 'rental income', 'lifestyle upgrade'"]
    }},
    "financial": {{
        "budget_min": 0,
        "budget_max": 0,
        "payment_preference": "string or null — 'cash', 'mortgage', 'payment plan', 'flexible'",
        "is_flexible": false
    }},
    "lifestyle": {{
        "household_composition": "string or null — e.g., 'couple', 'family with 2 kids', 'single professional'",
        "lifestyle_tags": ["list of strings — e.g., 'luxury', 'wellness', 'active', 'nightlife', 'golf'"],
        "must_have_amenities": ["list of strings — e.g., 'gym', 'spa', 'pool', 'concierge'"],
        "deal_breaker_features": ["list of strings or empty"]
    }},
    "engagement": {{
        "trust_level": "string — 'hot', 'warm', 'lukewarm', 'cold'",
        "lead_source": "string or null — 'broker referral', 'direct', 'online",
        "prior_interactions_count": 0,
        "decision_makers": ["list of strings — e.g., 'buyer', 'spouse', 'business partner'"]
    }},
    "property_fit": {{
        "unit_type": "string or null — 'apartment', 'penthouse', 'villa', 'townhouse', 'any'",
        "floor_preference": "string or null — 'high floor', 'mid floor', 'any'",
        "view_preference": "string or null — 'sea view', 'city view', 'any'",
        "ready_vs_offplan": "string or null — 'ready', 'off-plan', 'either'"
    }},
    "communication": {{
        "preferred_channel": "string or null",
        "best_time_to_reach": "string or null",
        "language_for_pitch": "string or null — infer from nationality/context"
    }},
    "ai_persona_label": "string — punchy one-liner (see rubric above)",
    "ai_recommended_angle": "string — specific pitch strategy (see rubric above)",
    "ai_recommended_persona_type": "string — one of: investor | end_user | investor_end_user | luxury_lifestyle | family | expat_relocator | corporate",
    "next_best_action": "string — concrete next step (see rubric above)",
    "trust_level_score": 0
}}

Return ONLY valid JSON. No markdown fences, no commentary, no explanation.
"""


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
        property_id=session.get("property_id"),
        lead_name=session.get("lead_name"),
        identity=persona_data.get("identity", {}),
        motivation=persona_data.get("motivation", {}),
        financial=persona_data.get("financial", {}),
        lifestyle=persona_data.get("lifestyle", {}),
        engagement=persona_data.get("engagement", {}),
        property_fit=persona_data.get("property_fit", {}),
        communication=persona_data.get("communication", {}),
        ai_persona_label=persona_data.get("ai_persona_label"),
        ai_recommended_angle=persona_data.get("ai_recommended_angle"),
        ai_recommended_persona_type=persona_data.get("ai_recommended_persona_type"),
        next_best_action=persona_data.get("next_best_action"),
        trust_level_score=persona_data.get("trust_level_score", 50),
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
