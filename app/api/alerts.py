from typing import Dict, List
from uuid import uuid4
from fastapi import APIRouter, HTTPException

from app.models.alert import Alert, AlertCreate, AlertStatus
from app.models.playbook import PlaybookExecutionResult
from app.services.enrichment import enrichment_service
from app.services.playbook_engine import playbook_engine
from app.services.metrics import ALERTS_CREATED, ALERTS_ENRICHED

router = APIRouter(prefix="/alerts", tags=["Alerts"])

# In-memory storage (we'll replace with a database later)
alerts_db: Dict[str, Alert] = {}


@router.post("/", response_model=Alert)
def create_alert(alert_data: AlertCreate) -> Alert:
    """Submit a new security alert for processing."""
    alert_id = str(uuid4())
    
    alert = Alert(
        id=alert_id,
        **alert_data.model_dump()
    )
    
    alerts_db[alert_id] = alert
    
    # Track metric
    ALERTS_CREATED.labels(
        severity=alert.severity.value,
        source=alert.source.value
    ).inc()
    
    return alert


@router.get("/", response_model=List[Alert])
def list_alerts() -> List[Alert]:
    """Get all alerts."""
    return list(alerts_db.values())


@router.get("/{alert_id}", response_model=Alert)
def get_alert(alert_id: str) -> Alert:
    """Get a specific alert by ID."""
    if alert_id not in alerts_db:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alerts_db[alert_id]


@router.patch("/{alert_id}/status", response_model=Alert)
def update_alert_status(alert_id: str, status: AlertStatus) -> Alert:
    """Update the status of an alert."""
    if alert_id not in alerts_db:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alerts_db[alert_id].status = status
    return alerts_db[alert_id]


@router.post("/{alert_id}/enrich", response_model=Alert)
async def enrich_alert(alert_id: str) -> Alert:
    """Enrich an alert with threat intelligence data."""
    if alert_id not in alerts_db:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert = alerts_db[alert_id]
    alert.status = AlertStatus.PROCESSING
    
    # Perform enrichment
    enrichment_data = await enrichment_service.enrich_alert(alert)
    
    # Update alert with enrichment data
    alert.enrichment_data = enrichment_data
    alert.status = AlertStatus.ENRICHED
    
    # Track metric
    ALERTS_ENRICHED.inc()
    
    return alert


@router.post("/{alert_id}/run-playbooks", response_model=List[PlaybookExecutionResult])
async def run_playbooks(alert_id: str) -> List[PlaybookExecutionResult]:
    """Run all matching playbooks for an alert."""
    if alert_id not in alerts_db:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert = alerts_db[alert_id]
    results = await playbook_engine.run_playbooks_for_alert(alert)
    
    if not results:
        raise HTTPException(status_code=404, detail="No matching playbooks found for this alert")
    
    return results