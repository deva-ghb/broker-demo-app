"""
Knowledge Base service — retrieves property context from MongoDB.
Uses native Atlas Search $vectorSearch for semantic relevance.
"""
from typing import List, Dict, Any, Optional
from services.database import get_collection
from services.ai_client import ai_client
from models.property import PROPERTY_COLLECTION


async def get_property_context(property_id: str) -> Dict[str, Any]:
    """
    Fetch full property details from MongoDB for the AI system prompt.
    """
    collection = get_collection(PROPERTY_COLLECTION)
    prop = await collection.find_one({"property_id": property_id})
    if not prop:
        return {}

    # Remove MongoDB internal fields
    prop.pop("_id", None)
    return prop


async def search_relevant_properties(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Semantic search for relevant properties using MongoDB vectors and cosine similarity.
    """
    try:
        query_vector = ai_client.get_embedding(query)
        collection = get_collection(PROPERTY_COLLECTION)
        
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "description_vector_index",
                    "path": "description_vector",
                    "queryVector": query_vector,
                    "numCandidates": 10,
                    "limit": top_k
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "description_vector": 0,
                    "amenities_vector": 0
                }
            }
        ]
        
        properties = []
        cursor = collection.aggregate(pipeline)
        async for prop in cursor:
            properties.append(prop)
            
        return properties
        
    except Exception as e:
        print(f"⚠️ Knowledge base $vectorSearch failed: {e}")
        return []


def build_property_context_prompt(property_data: Dict[str, Any]) -> str:
    """
    Format property data into a context string for the AI system prompt.
    """
    if not property_data:
        return "No specific property context available."

    lines = [f"**Property: {property_data.get('name', 'Unknown')}**"]

    if property_data.get("developer"):
        lines.append(f"- Developer: {property_data['developer']}")
    if property_data.get("location"):
        lines.append(f"- Location: {property_data['location']}")
    if property_data.get("property_type"):
        lines.append(f"- Type: {property_data['property_type']}")
    if property_data.get("usps"):
        lines.append(f"- USPs: {', '.join(property_data['usps'])}")
    if property_data.get("price_range"):
        lines.append(f"- Price Range: {property_data['price_range']}")
    if property_data.get("payment_plans"):
        lines.append(f"- Payment Plans: {property_data['payment_plans']}")
    if property_data.get("golden_visa_eligible"):
        lines.append("- ✅ Golden Visa Eligible")
    if property_data.get("projected_roi"):
        lines.append(f"- Projected ROI: {property_data['projected_roi']}")

    # Include asset descriptions
    assets = property_data.get("assets", [])
    if assets:
        lines.append("\n**Available Assets:**")
        for asset in assets[:10]:  # Limit to avoid prompt bloat
            lines.append(f"- [{asset.get('type', 'unknown')}] {asset.get('description', '')}")

    return "\n".join(lines)
