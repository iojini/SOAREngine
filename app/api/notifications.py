from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.api_key import verify_api_key
from app.database.db import get_db
from app.database.repository import AlertRepository
from app.services.notifications import notification_service

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
    dependencies=[Depends(verify_api_key)]
)


class SlackNotificationRequest(BaseModel):
    """Request body for sending a Slack notification."""
    message: str
    channel: Optional[str] = None
    alert_id: Optional[str] = None


class NotificationResponse(BaseModel):
    """Response from sending a notification."""
    success: bool
    channel: str
    message: str
    error: Optional[str] = None


@router.post("/slack", response_model=NotificationResponse)
async def send_slack_notification(
    request: SlackNotificationRequest,
    db: AsyncSession = Depends(get_db)
) -> NotificationResponse:
    """Send a notification to Slack."""
    alert = None
    
    if request.alert_id:
        repo = AlertRepository(db)
        alert = await repo.get_by_id(request.alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
    
    result = await notification_service.send_slack_notification(
        message=request.message,
        channel=request.channel,
        alert=alert
    )
    
    return NotificationResponse(**result)


@router.post("/alerts/{alert_id}/notify", response_model=NotificationResponse)
async def notify_alert(
    alert_id: str,
    channel: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> NotificationResponse:
    """Send a Slack notification for a specific alert."""
    repo = AlertRepository(db)
    alert = await repo.get_by_id(alert_id)
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    result = await notification_service.send_alert_notification(alert, channel)
    
    return NotificationResponse(**result)