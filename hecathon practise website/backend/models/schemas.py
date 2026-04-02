from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

# AREA SELECTION
class AreaSelectionRequest(BaseModel):
    geojson: Dict[str, Any] = Field(..., description="GeoJSON Polygon of the selected area")

class TileCoordinate(BaseModel):
    id: str
    xmin: float
    ymin: float
    xmax: float
    ymax: float
    center: List[float]

class AreaSelectionResponse(BaseModel):
    tiles: List[TileCoordinate]
    total_tiles: int

# SATELLITE DATA
class SatelliteDataRequest(BaseModel):
    tile_id: str
    before_date: str = "2023-01-01"
    after_date: str = "2024-01-01"
    cloud_cover: float = 10.0

class SatelliteDataResponse(BaseModel):
    tile_id: str
    before_url: str
    after_url: str
    metadata: Dict[str, Any]

# CHANGE DETECTION
class DetectChangeRequest(BaseModel):
    tile_id: str
    before_url: str
    after_url: str
    lat: Optional[float] = 23.0
    lon: Optional[float] = 72.5

class DetectionResult(BaseModel):
    label: str
    confidence: float
    area_sqm: float
    geometry_geojson: Dict[str, Any]

class DetectChangeResponse(BaseModel):
    tile_id: str
    changes: List[DetectionResult]
    summary: str

# COMPLIANCE CHECK
class ComplianceCheckRequest(BaseModel):
    tile_id: str
    detection_results: List[DetectionResult]
    zoning_rules: Optional[str] = "AUDA_2024"

class Violation(BaseModel):
    type: str
    status: str  # Violation / Authorized
    severity: str  # High / Medium / Low
    reason: str

class ComplianceCheckResponse(BaseModel):
    tile_id: str
    violations: List[Violation]

# REPORT GENERATION
class GenerateReportRequest(BaseModel):
    tile_id: str
    area_name: Optional[str] = "Unnamed Zone"
    detection_results: List[DetectionResult]
    violations: List[Violation]
    user_id: str = "guest"

class GenerateReportResponse(BaseModel):
    report_id: str
    download_url: str
    message: str
