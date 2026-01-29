from typing import Dict, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key import verify_api_key
from app.database.db import get_db
from app.database.models import AlertDB

router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"],
    dependencies=[Depends(verify_api_key)]
)


class AlertStats(BaseModel):
    """Overall alert statistics."""
    total_alerts: int
    by_severity: Dict[str, int]
    by_source: Dict[str, int]
    by_status: Dict[str, int]


class TimeSeriesPoint(BaseModel):
    """A single point in time series data."""
    date: str
    count: int


class DashboardStats(BaseModel):
    """Dashboard-ready statistics."""
    total_alerts: int
    critical_alerts: int
    high_alerts: int
    pending_alerts: int
    enriched_alerts: int
    alerts_today: int
    alerts_this_week: int


@router.get("/alerts", response_model=AlertStats)
async def get_alert_statistics(
    db: AsyncSession = Depends(get_db)
) -> AlertStats:
    """Get overall alert statistics."""
    
    # Total alerts
    total_result = await db.execute(select(func.count(AlertDB.id)))
    total_alerts = total_result.scalar() or 0
    
    # By severity
    severity_result = await db.execute(
        select(AlertDB.severity, func.count(AlertDB.id))
        .group_by(AlertDB.severity)
    )
    by_severity = {row[0]: row[1] for row in severity_result.fetchall()}
    
    # By source
    source_result = await db.execute(
        select(AlertDB.source, func.count(AlertDB.id))
        .group_by(AlertDB.source)
    )
    by_source = {row[0]: row[1] for row in source_result.fetchall()}
    
    # By status
    status_result = await db.execute(
        select(AlertDB.status, func.count(AlertDB.id))
        .group_by(AlertDB.status)
    )
    by_status = {row[0]: row[1] for row in status_result.fetchall()}
    
    return AlertStats(
        total_alerts=total_alerts,
        by_severity=by_severity,
        by_source=by_source,
        by_status=by_status
    )


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_statistics(
    db: AsyncSession = Depends(get_db)
) -> DashboardStats:
    """Get dashboard-ready statistics."""
    
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    
    # Total alerts
    total_result = await db.execute(select(func.count(AlertDB.id)))
    total_alerts = total_result.scalar() or 0
    
    # Critical alerts
    critical_result = await db.execute(
        select(func.count(AlertDB.id))
        .where(AlertDB.severity == "critical")
    )
    critical_alerts = critical_result.scalar() or 0
    
    # High alerts
    high_result = await db.execute(
        select(func.count(AlertDB.id))
        .where(AlertDB.severity == "high")
    )
    high_alerts = high_result.scalar() or 0
    
    # Pending alerts
    pending_result = await db.execute(
        select(func.count(AlertDB.id))
        .where(AlertDB.status == "pending")
    )
    pending_alerts = pending_result.scalar() or 0
    
    # Enriched alerts
    enriched_result = await db.execute(
        select(func.count(AlertDB.id))
        .where(AlertDB.status == "enriched")
    )
    enriched_alerts = enriched_result.scalar() or 0
    
    # Alerts today
    today_result = await db.execute(
        select(func.count(AlertDB.id))
        .where(AlertDB.created_at >= today_start)
    )
    alerts_today = today_result.scalar() or 0
    
    # Alerts this week
    week_result = await db.execute(
        select(func.count(AlertDB.id))
        .where(AlertDB.created_at >= week_start)
    )
    alerts_this_week = week_result.scalar() or 0
    
    return DashboardStats(
        total_alerts=total_alerts,
        critical_alerts=critical_alerts,
        high_alerts=high_alerts,
        pending_alerts=pending_alerts,
        enriched_alerts=enriched_alerts,
        alerts_today=alerts_today,
        alerts_this_week=alerts_this_week
    )


@router.get("/top-source-ips", response_model=List[Dict])
async def get_top_source_ips(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
) -> List[Dict]:
    """Get top source IPs by alert count."""
    
    result = await db.execute(
        select(AlertDB.source_ip, func.count(AlertDB.id).label("count"))
        .where(AlertDB.source_ip.isnot(None))
        .group_by(AlertDB.source_ip)
        .order_by(func.count(AlertDB.id).desc())
        .limit(limit)
    )
    
    return [{"source_ip": row[0], "count": row[1]} for row in result.fetchall()]