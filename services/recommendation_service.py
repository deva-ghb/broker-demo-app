"""
Property Recommendation Service.
Extracts search filters via LLM and applies them via MongoDB semantic search.
Uses pure Python cosine similarity, dropping Qdrant to simplify infrastructure.
"""
import json
import math
from typing import List, Dict, Any, Tuple, Optional

from services.database import get_collection
from services.ai_client import ai_client
from models.property import PROPERTY_COLLECTION
from models.persona import PERSONA_COLLECTION

# Fallback property if search yields 0 results
DEFAULT_PROPERTY_ID = "prop_treppan_serenique"

from pydantic import BaseModel

class FilterCriteria(BaseModel):
    budget_min_aed_million: Optional[float] = None
    budget_max_aed_million: Optional[float] = None
    semantic_query: str

FILTER_EXTRACTION_PROMPT = """You are a real estate search assistant.
Given the following buyer persona, extract the search criteria to find the right property.
You must return a JSON object with EXACTLY these fields:
{{
    "budget_min_aed_million": <float or null if not specified>,
    "budget_max_aed_million": <float or null if not specified>,
    "semantic_query": "<A single descriptive string combining the user's lifestyle preferences, key interests, and desired amenities to use for vector search>"
}}

Persona:
{persona_json}
"""


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)


async def get_embedding(text: str) -> List[float]:
    """Generate an embedding for a text string using the AI client."""
    # Run synchronously because ai_client.get_embedding is sync
    return ai_client.get_embedding(text)


async def _extract_filters(persona_data: Dict[str, Any]) -> Dict[str, Any]:
    """Use LLM to extract hard filters and semantic query from Persona."""
    # Remove non-serializable fields for JSON
    clean_persona = {k: v for k, v in persona_data.items() if k not in ['created_at', '_id']}
    persona_str = json.dumps(clean_persona, indent=2, default=str)
    messages = [
        {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
        {"role": "user", "content": FILTER_EXTRACTION_PROMPT.format(persona_json=persona_str)}
    ]
    
    try:
        result_text = ai_client.structured_completion(messages, response_structure=FilterCriteria)
        filters = json.loads(result_text)
        return filters
    except Exception as e:
        print(f"Error parsing LLM filter extraction: {e}")
        return {
            "budget_min_aed_million": None,
            "budget_max_aed_million": None,
            "semantic_query": persona_data.get("primary_motivation", "luxury real estate")
        }


async def recommend_properties(persona_id: str = None, persona_json: Dict[str, Any] = None) -> Tuple[List[str], Dict[str, Any]]:
    """
    Recommend properties by generating an embedding for the persona's semantic needs
    and filtering by their budget against MongoDB documents.
    """
    persona_data = persona_json or {}
    
    if persona_id and not persona_json:
        # Load from DB
        collection = get_collection(PERSONA_COLLECTION)
        doc = await collection.find_one({"persona_id": persona_id})
        if doc:
            doc.pop("_id", None)
            persona_data = doc

    if not persona_data:
        print("No persona data found, returning default.")
        return [DEFAULT_PROPERTY_ID], {}

    # 1. Extract filters using LLM
    filters = await _extract_filters(persona_data)
    
    budget_min = filters.get("budget_min_aed_million")
    budget_max = filters.get("budget_max_aed_million")
    semantic_query = filters.get("semantic_query") or "nice property"
    
    # 2. Get embedding for the semantic query
    query_vector = await get_embedding(semantic_query)
    
    # 3. Build MongoDB hard filters for the vectorSearch pre-filter
    filter_conditions = {}
    
    if budget_max is not None:
        filter_conditions["price_start_aed_in_million"] = {"$lte": budget_max}
    if budget_min is not None:
        filter_conditions["price_end_aed_in_million"] = {"$gte": budget_min}

    # 4. Fetch matching properties using $vectorSearch natively
    collection = get_collection(PROPERTY_COLLECTION)
    
    pipeline = [
        {
            "$vectorSearch": {
                "index": "description_vector_index",
                "path": "description_vector",
                "queryVector": query_vector,
                "numCandidates": 20,
                "limit": 5,
                "filter": filter_conditions if filter_conditions else None
            }
        },
        {
            "$project": {
                "property_id": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    
    # Remove filter arg if empty because $vectorSearch strict syntax
    if not filter_conditions:
        del pipeline[0]["$vectorSearch"]["filter"]

    scored_props = []
    try:
        cursor = collection.aggregate(pipeline)
        async for prop in cursor:
            scored_props.append((prop["property_id"], prop.get("score", 0)))
    except Exception as e:
        print(f"Atlas Vector Search failed: {e}. Ensure you are using mongodb-atlas-local and the 'description_vector_index' is created.")
        
    # Sort and return
    recommended_ids = [p[0] for p in scored_props if p[1] > 0.0]
    
    if not recommended_ids:
        print(f"No properties matched filters/semantics natively, falling back.")
        return [DEFAULT_PROPERTY_ID], filters
        
    return recommended_ids, filters
