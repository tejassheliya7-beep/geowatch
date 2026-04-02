from fastapi import APIRouter, HTTPException
from models.schemas import DetectChangeRequest, DetectChangeResponse, DetectionResult
from services.ai_model import ChangeFormerWrapper

router = APIRouter(prefix="/detection", tags=["AI Change Detection"])

@router.post("/detect-change", response_model=DetectChangeResponse)
async def detect_change(request: DetectChangeRequest):
    """
    Perform AI-based change detection comparing 'before' and 'after' satellite imagery.
    Uses pre-trained ChangeFormer model.
    """
    try:
        # Load and use AI model
        ai_model = ChangeFormerWrapper()
        
        # In a real app, you'd download the images from request.before_url/after_url
        # to a local path or pre-process from a direct URL stream.
        # For demo, using mock predict results:
        results = ai_model.predict(request.before_url, request.after_url, lat=request.lat, lon=request.lon)
        
        if "error" in results:
            raise HTTPException(status_code=500, detail=results.get("error"))
            
        changes = [
            DetectionResult(
                label=c.get("label"),
                confidence=c.get("confidence"),
                area_sqm=c.get("area_sqm"),
                geometry_geojson=c.get("geometry_geojson")
            ) for c in results.get("changes", [])
        ]
        
        return DetectChangeResponse(
            tile_id=request.tile_id,
            changes=changes,
            summary=results.get("summary", "Done.")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
