import httpx
from typing import Optional

from app.config import get_settings
from app.models.alert import Alert


class NotificationService:
    """Service for sending notifications to external systems."""
    
    def __init__(self):
        settings = get_settings()
        self.slack_webhook_url = settings.slack_webhook_url
        self.default_channel = settings.slack_default_channel
    
    async def send_slack_notification(
        self,
        message: str,
        channel: Optional[str] = None,
        alert: Optional[Alert] = None
    ) -> dict:
        """Send a notification to Slack."""
        result = {
            "success": False,
            "channel": channel or self.default_channel,
            "message": "",
            "error": None
        }
        
        if not self.slack_webhook_url:
            result["message"] = "Slack notification simulated (no webhook configured)"
            result["success"] = True
            return result
        
        payload = self._build_slack_payload(message, channel, alert)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.slack_webhook_url,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result["success"] = True
                    result["message"] = "Notification sent successfully"
                else:
                    result["error"] = f"Slack returned status {response.status_code}"
                    
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _build_slack_payload(
        self,
        message: str,
        channel: Optional[str] = None,
        alert: Optional[Alert] = None
    ) -> dict:
        """Build a Slack message payload."""
        payload = {
            "channel": channel or self.default_channel,
            "username": "SOAREngine",
            "icon_emoji": ":shield:",
            "text": message
        }
        
        if alert:
            severity_emoji = {
                "low": "🟢",
                "medium": "🟡", 
                "high": "🟠",
                "critical": "🔴"
            }.get(alert.severity.value if hasattr(alert.severity, 'value') else alert.severity, "⚪")
            
            severity_val = alert.severity.value if hasattr(alert.severity, 'value') else alert.severity
            source_val = alert.source.value if hasattr(alert.source, 'value') else alert.source
            status_val = alert.status.value if hasattr(alert.status, 'value') else alert.status
            
            payload["attachments"] = [{
                "color": self._get_severity_color(severity_val),
                "fields": [
                    {"title": "Alert", "value": f"{severity_emoji} {alert.title}", "short": False},
                    {"title": "Severity", "value": severity_val, "short": True},
                    {"title": "Source", "value": source_val, "short": True},
                    {"title": "Status", "value": status_val, "short": True},
                    {"title": "Alert ID", "value": alert.id, "short": True}
                ]
            }]
            
            if alert.source_ip:
                payload["attachments"][0]["fields"].append(
                    {"title": "Source IP", "value": alert.source_ip, "short": True}
                )
        
        return payload
    
    def _get_severity_color(self, severity: str) -> str:
        """Get Slack attachment color based on severity."""
        colors = {
            "low": "#36a64f",
            "medium": "#ffcc00",
            "high": "#ff9900",
            "critical": "#ff0000"
        }
        return colors.get(severity, "#808080")
    
    async def send_alert_notification(self, alert: Alert, channel: Optional[str] = None) -> dict:
        """Send a formatted alert notification to Slack."""
        message = f"New security alert: {alert.title}"
        return await self.send_slack_notification(message, channel, alert)


# Global instance
notification_service = NotificationService()