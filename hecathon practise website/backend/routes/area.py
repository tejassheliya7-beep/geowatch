from fastapi import APIRouter, HTTPException
from models.schemas import AreaSelectionRequest, AreaSelectionResponse, TileCoordinate
from services.grid_service import GridService

router = APIRouter(prefix="/area", tags=["Area Selection"])

@router.post("/select-area", response_model=AreaSelectionResponse)
async def select_area(request: AreaSelectionRequest):
    """
    Divide a selected GeoJSON polygon into 1km x 1km grid tiles.
    """
    try:
        grid_svc = GridService()
        tiles_raw = grid_svc.generate_grid(request.geojson)
        
        if not tiles_raw:
            raise HTTPException(status_code=400, detail="Invalid GeoJSON or area too small for tiling.")
            
        tiles = [
            TileCoordinate(
                id=t["id"],
                xmin=t["xmin"],
                ymin=t["ymin"],
                xmax=t["xmax"],
                ymax=t["ymax"],
                center=t["center"]
            ) for t in tiles_raw
        ]
        
        return AreaSelectionResponse(tiles=tiles, total_tiles=len(tiles))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
