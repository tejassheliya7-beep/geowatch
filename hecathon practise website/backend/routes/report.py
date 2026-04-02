from fastapi import APIRouter, HTTPException
from models.schemas import GenerateReportRequest, GenerateReportResponse
from services.report_service import ReportService
import os

router = APIRouter(prefix="/report", tags=["Report Generation"])

@router.post("/generate-report", response_model=GenerateReportResponse)
async def generate_report(request: GenerateReportRequest):
    """
    Generate a downloadable PDF report summarizing the detection and compliance status.
    """
    try:
        report_svc = ReportService()
        
        # Prepare inputs
        raw_detections = [d.dict() for d in request.detection_results]
        raw_violations = [v.dict() for v in request.violations]
        
        # Generate the file
        local_path = report_svc.generate_pdf(
            request.tile_id, 
            raw_detections, 
            raw_violations, 
            area_name=request.area_name
        )
        
        # In production, you'd upload this to an S3/Cloud Storage and return the URL
        # For demo, return a logical local download path
        download_url = f"/static/{os.path.basename(local_path)}"
        
        return GenerateReportResponse(
            report_id=f"rep_{request.tile_id}",
            download_url=download_url,
            message="Report generated successfully."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
