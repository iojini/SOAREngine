from typing import List
from fastapi import Request
from app.rate_limit import limiter
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key import verify_api_key
from app.database.db import get_db
from app.database.repository import AlertRepository
from app.models.alert import Alert, AlertCreate, AlertStatus
from app.models.playbook import PlaybookExecutionResult
from app.services.enrichment import enrichment_service
from app.services.playbook_engine import playbook_engine
from app.services.metrics import ALERTS_CREATED, ALERTS_ENRICHED

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
    dependencies=[Depends(verify_api_key)]
)


@router.post("/", response_model=Alert)
@limiter.limit("30/minute")
async def create_alert(
    request: Request,
    alert_data: AlertCreate,
    db: AsyncSession = Depends(get_db)
) -> Alert:
    """Submit a new security alert for processing."""
    repo = AlertRepository(db)
    alert = await repo.create(alert_data)
    
    # Track metric
    ALERTS_CREATED.labels(
        severity=alert.severity.value,
        source=alert.source.value
    ).inc()
    
    return alert


@router.get("/", response_model=List[Alert])
async def list_alerts(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
) -> List[Alert]:
    """Get all alerts with pagination."""
    repo = AlertRepository(db)
    return await repo.get_all(limit=limit, offset=offset)


@router.get("/{alert_id}", response_model=Alert)
async def get_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
) -> Alert:
    """Get a specific alert by ID."""
    repo = AlertRepository(db)
    alert = await repo.get_by_id(alert_id)
    
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return alert


@router.patch("/{alert_id}/status", response_model=Alert)
async def update_alert_status(
    alert_id: str,
    status: AlertStatus,
    db: AsyncSession = Depends(get_db)
) -> Alert:
    """Update the status of an alert."""
    repo = AlertRepository(db)
    alert = await repo.update_status(alert_id, status)
    
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return alert


@router.post("/{alert_id}/enrich", response_model=Alert)
async def enrich_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
) -> Alert:
    """Enrich an alert with threat intelligence data."""
    repo = AlertRepository(db)
    alert = await repo.get_by_id(alert_id)
    
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Update status to processing
    await repo.update_status(alert_id, AlertStatus.PROCESSING)
    
    # Perform enrichment
    enrichment_data = await enrichment_service.enrich_alert(alert)
    
    # Update alert with enrichment data
    alert = await repo.update_enrichment(alert_id, enrichment_data)
    
    # Track metric
    ALERTS_ENRICHED.inc()
    
    return alert


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Delete an alert."""
    repo = AlertRepository(db)
    deleted = await repo.delete(alert_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert deleted successfully"}


@router.post("/{alert_id}/run-playbooks", response_model=List[PlaybookExecutionResult])
async def run_playbooks(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[PlaybookExecutionResult]:
    """Run all matching playbooks for an alert."""
    repo = AlertRepository(db)
    alert = await repo.get_by_id(alert_id)
    
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    results = await playbook_engine.run_playbooks_for_alert(alert)
    
    if not results:
        raise HTTPException(status_code=404, detail="No matching playbooks found for this alert")
    
    return results