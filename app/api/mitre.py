from typing import List
from fastapi import APIRouter, HTTPException

from app.models.mitre import MitreTechnique, AlertMitreMapping
from app.services.mitre_mapper import mitre_mapper
from app.api.alerts import alerts_db

router = APIRouter(prefix="/mitre", tags=["MITRE ATT&CK"])


@router.get("/techniques", response_model=List[MitreTechnique])
def list_techniques() -> List[MitreTechnique]:
    """List all available MITRE ATT&CK techniques."""
    return mitre_mapper.list_techniques()


@router.get("/techniques/{technique_id}", response_model=MitreTechnique)
def get_technique(technique_id: str) -> MitreTechnique:
    """Get a specific MITRE ATT&CK technique by ID."""
    technique = mitre_mapper.get_technique(technique_id)
    if not technique:
        raise HTTPException(status_code=404, detail="Technique not found")
    return technique


@router.get("/tactics/{tactic}/techniques", response_model=List[MitreTechnique])
def get_techniques_by_tactic(tactic: str) -> List[MitreTechnique]:
    """Get all techniques for a specific tactic."""
    techniques = mitre_mapper.get_techniques_by_tactic(tactic)
    if not techniques:
        raise HTTPException(status_code=404, detail="No techniques found for this tactic")
    return techniques


@router.post("/alerts/{alert_id}/map", response_model=AlertMitreMapping)
def map_alert_to_mitre(alert_id: str) -> AlertMitreMapping:
    """Map an alert to MITRE ATT&CK techniques."""
    if alert_id not in alerts_db:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert = alerts_db[alert_id]
    mapping = mitre_mapper.map_alert(alert)
    return mapping