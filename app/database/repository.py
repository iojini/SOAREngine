import json
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import AlertDB
from app.models.alert import Alert, AlertCreate, AlertStatus


class AlertRepository:
    """Repository for alert database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, alert_data: AlertCreate) -> Alert:
        """Create a new alert in the database."""
        alert_id = str(uuid4())
        
        db_alert = AlertDB(
            id=alert_id,
            title=alert_data.title,
            description=alert_data.description,
            severity=alert_data.severity.value,
            source=alert_data.source.value,
            source_ip=alert_data.source_ip,
            destination_ip=alert_data.destination_ip,
            domain=alert_data.domain,
            file_hash=alert_data.file_hash,
            status=AlertStatus.PENDING.value
        )
        
        self.session.add(db_alert)
        await self.session.commit()
        await self.session.refresh(db_alert)
        
        return self._to_alert(db_alert)
    
    async def get_by_id(self, alert_id: str) -> Optional[Alert]:
        """Get an alert by ID."""
        result = await self.session.execute(
            select(AlertDB).where(AlertDB.id == alert_id)
        )
        db_alert = result.scalar_one_or_none()
        
        if db_alert is None:
            return None
        
        return self._to_alert(db_alert)
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Alert]:
        """Get all alerts with pagination."""
        result = await self.session.execute(
            select(AlertDB)
            .order_by(AlertDB.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        db_alerts = result.scalars().all()
        
        return [self._to_alert(db_alert) for db_alert in db_alerts]
    
    async def update_status(self, alert_id: str, status: AlertStatus) -> Optional[Alert]:
        """Update an alert's status."""
        result = await self.session.execute(
            select(AlertDB).where(AlertDB.id == alert_id)
        )
        db_alert = result.scalar_one_or_none()
        
        if db_alert is None:
            return None
        
        db_alert.status = status.value
        await self.session.commit()
        await self.session.refresh(db_alert)
        
        return self._to_alert(db_alert)
    
    async def update_enrichment(self, alert_id: str, enrichment_data: dict) -> Optional[Alert]:
        """Update an alert's enrichment data."""
        result = await self.session.execute(
            select(AlertDB).where(AlertDB.id == alert_id)
        )
        db_alert = result.scalar_one_or_none()
        
        if db_alert is None:
            return None
        
        db_alert.enrichment_data = json.dumps(enrichment_data)
        db_alert.status = AlertStatus.ENRICHED.value
        await self.session.commit()
        await self.session.refresh(db_alert)
        
        return self._to_alert(db_alert)
    
    async def delete(self, alert_id: str) -> bool:
        """Delete an alert."""
        result = await self.session.execute(
            select(AlertDB).where(AlertDB.id == alert_id)
        )
        db_alert = result.scalar_one_or_none()
        
        if db_alert is None:
            return False
        
        await self.session.delete(db_alert)
        await self.session.commit()
        return True
    
    def _to_alert(self, db_alert: AlertDB) -> Alert:
        """Convert database model to Pydantic model."""
        enrichment = None
        if db_alert.enrichment_data:
            try:
                enrichment = json.loads(db_alert.enrichment_data)
            except json.JSONDecodeError:
                enrichment = None
        
        return Alert(
            id=db_alert.id,
            title=db_alert.title,
            description=db_alert.description,
            severity=db_alert.severity,
            source=db_alert.source,
            source_ip=db_alert.source_ip,
            destination_ip=db_alert.destination_ip,
            domain=db_alert.domain,
            file_hash=db_alert.file_hash,
            status=db_alert.status,
            created_at=db_alert.created_at,
            enrichment_data=enrichment
        )