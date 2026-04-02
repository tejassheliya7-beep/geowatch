from fastapi import APIRouter, HTTPException
from models.schemas import SatelliteDataRequest, SatelliteDataResponse
from services.gee_service import GEEService

router = APIRouter(prefix="/satellite", tags=["Satellite Data Fetch"])

@router.get("/satellite-data", response_model=SatelliteDataResponse)
async def get_satellite_data(tile_id: str, before_date: str = "2023-01-01", after_date: str = "2024-01-01"):
    """
    Fetch Sentinel-2 satellite imagery for a given tile ID and date ranges via Google Earth Engine.
    """
    try:
        # Initializing GEE Service
        gee_svc = GEEService()
        
        # Tile coordinates - fetch from mock db or cache for the tile_id
        # For demo, using Ahmedabad coordinates:
        tile_coords = [72.5, 23.0, 72.6, 23.1]
        
        # Create a search window (1 month before to the selected date) to ensure a valid range
        from datetime import datetime, timedelta
        def month_before(d_str):
            dt = datetime.strptime(d_str, "%Y-%m-%d")
            return (dt - timedelta(days=90)).strftime("%Y-%m-%d")

        # Fetch 'before' image (window of 90 days before the baseline)
        before_res = gee_svc.fetch_sentinel_data(tile_coords, month_before(before_date), before_date)
        # Fetch 'after' image (window of 90 days before the comparison)
        after_res = gee_svc.fetch_sentinel_data(tile_coords, month_before(after_date), after_date)
        
        if "error" in before_res or "error" in after_res:
             raise HTTPException(status_code=500, detail="GEE interaction failed.")
             
        return SatelliteDataResponse(
            tile_id=tile_id,
            before_url=before_res.get("image_url", ""),
            after_url=after_res.get("image_url", ""),
            metadata=after_res.get("metadata", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
