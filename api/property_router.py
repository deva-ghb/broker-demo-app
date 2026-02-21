from fastapi import APIRouter
from typing import List, Dict, Any
from services.database import get_collection
from models.property import PROPERTY_COLLECTION

router = APIRouter(prefix="/api/v1/properties", tags=["Properties"])

@router.get("/", response_model=Dict[str, List[Dict[str, Any]]])
async def list_properties():
    """
    List all available properties (ID and Name) for UI dropdowns.
    """
    collection = get_collection(PROPERTY_COLLECTION)
    cursor = collection.find({}, {"property_id": 1, "name": 1, "_id": 0})
    properties = []
    async for prop in cursor:
        properties.append(prop)
    
    return {"properties": properties}
