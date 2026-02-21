"""
Microsite Builder API router.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from schemas.microsite_schemas import MicrositeBuildRequest, MicrositeBuildResponse
from services.microsite_service import build_microsite, get_microsite_html
from services.recommendation_service import recommend_properties

router = APIRouter(tags=["Microsite Builder"])


@router.post("/api/v1/microsite/build", response_model=MicrositeBuildResponse)
async def build_microsite_endpoint(request: MicrositeBuildRequest):
    """
    Generate a personalized microsite for a persona + property combination.
    If property_id is None, uses Recommendation Service to find best match.
    Returns the unique URL and tracking ID.
    """
    try:
        prop_id = request.property_id
        if not prop_id:
            recommended_ids, _ = await recommend_properties(persona_id=request.persona_id)
            prop_id = recommended_ids[0]
            
        result = await build_microsite(
            persona_id=request.persona_id,
            property_id=prop_id,
        )
        return MicrositeBuildResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build microsite: {str(e)}")


@router.get("/m/{persona_id}", response_class=HTMLResponse)
async def serve_microsite(persona_id: str):
    """
    Serve the rendered microsite HTML.
    This is the public-facing URL shared with buyers.
    """
    html = await get_microsite_html(persona_id)
    if not html:
        raise HTTPException(status_code=404, detail="Microsite not found")
    return HTMLResponse(content=html)
