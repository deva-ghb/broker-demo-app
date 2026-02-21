"""
Recommendation API router.
"""
from fastapi import APIRouter, HTTPException
from schemas.recommendation_schemas import RecommendationRequest, RecommendationResponse
from services.recommendation_service import recommend_properties

router = APIRouter(tags=["Recommendation Engine"])


@router.post("/api/v1/recommendation", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get property recommendations based on a persona's JSON context or ID.
    Used for intelligent matching inside the microsite builder or standalone tools.
    """
    if not request.persona_id and not request.persona_json:
        raise HTTPException(status_code=400, detail="Must provide either persona_id or persona_json")
        
    try:
        property_ids, filters = await recommend_properties(
            persona_id=request.persona_id,
            persona_json=request.persona_json
        )
        return RecommendationResponse(property_ids=property_ids, filter_criteria=filters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")
