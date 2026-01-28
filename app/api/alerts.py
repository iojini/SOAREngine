from typing import Dict, List
from uuid import uuid4
from fastapi import APIRouter, HTTPException

from app.models.alert import Alert, AlertCreate, AlertStatus

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