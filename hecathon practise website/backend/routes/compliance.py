from fastapi import APIRouter, HTTPException
from models.schemas import ComplianceCheckRequest, ComplianceCheckResponse, Violation
from services.compliance_service import ComplianceService

router = APIRouter(prefix="/compliance", tags=["Compliance Verification"])

@router.post("/compliance-check", response_model=ComplianceCheckResponse)
async def check_compliance(request: ComplianceCheckRequest):
    """
    Compare detected changes with zoning data (AUDA rules) to flag violations.
    """
    try:
        # Load and use compliance ruleset
        compliance_svc = ComplianceService(request.zoning_rules)
        
        # In a real app, detection_results would contain the predicted label geom
        raw_results = [r.dict() for r in request.detection_results]
        
        # Check violations
        raw_violations = compliance_svc.check_violations(request.tile_id, raw_results)
        
        violations = [
            Violation(
                type=v.get("type"),
                status=v.get("status"),
                severity=v.get("severity"),
                reason=v.get("reason")
            ) for v in raw_violations
        ]
        
        return ComplianceCheckResponse(
            tile_id=request.tile_id,
            violations=violations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
