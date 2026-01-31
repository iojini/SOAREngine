import httpx
import logging
from typing import Optional

from app.config import get_settings
from app.services.reliability import (
    dead_letter_queue,
    notification_circuit,
    with_retry,
    OperationType,
)

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications via Slack and other channels."""

    def __init__(self):
        settings = get_settings()
        self.slack_webhook_url: Optional[str] = settings.slack_webhook_url
        self.default_channel: str = settings.slack_default_channel

    @with_retry(max_attempts=3, min_wait=1, max_wait=10, exceptions=(httpx.HTTPError, httpx.TimeoutException))
    async def _send_slack_request(self, payload: dict) -> bool:
        """Send a Slack webhook request with retry logic."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.slack_webhook_url,
                json=payload,
                timeout=10.0
            )
            if response.status_code == 200:
                return True
            else:
                raise httpx.HTTPError(f"Slack returned status {response.status_code}")

    async def send_slack_notification(
        self,
        message: str,
        channel: Optional[str] = None,
        severity: Optional[str] = None,
        alert_id: Optional[str] = None
    ) -> dict:
        """Send a notification to Slack with circuit breaker protection."""
        result = {
            "success": False,
            "channel": channel or self.default_channel,
            "message": message,
            "error": None
        }

        if not self.slack_webhook_url:
            result["success"] = True
            result["note"] = "Mock notification - no Slack webhook configured"
            logger.info(f"Mock Slack notification: {message[:100]}")
            return result

        # Check circuit breaker
        if not await notification_circuit.can_execute():
            error_msg = "Circuit breaker open for notifications"
            logger.warning(error_msg)
            await dead_letter_queue.add(
                operation_type=OperationType.NOTIFICATION,
                payload={"message": message, "channel": channel},
                error=error_msg,
                alert_id=alert_id
            )
            result["error"] = error_msg
            return result

        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }

        emoji = severity_emoji.get(severity, "ℹ️")

        payload = {
            "channel": channel or self.default_channel,
            "username": "SOAREngine",
            "icon_emoji": ":shield:",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{emoji} SOAREngine Alert",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity:* {severity or 'N/A'} | *Channel:* {channel or self.default_channel}"
                        }
                    ]
                }
            ]
        }

        try:
            await self._send_slack_request(payload)
            await notification_circuit.record_success()
            result["success"] = True
            logger.info(f"Slack notification sent: {message[:100]}")
        except Exception as e:
            await notification_circuit.record_failure()
            await dead_letter_queue.add(
                operation_type=OperationType.NOTIFICATION,
                payload={"message": message, "channel": channel},
                error=str(e),
                alert_id=alert_id
            )
            result["error"] = str(e)
            logger.error(f"Failed to send Slack notification: {e}")

        return result

    async def notify_alert(self, alert) -> dict:
        """Send a notification about a specific alert."""
        message = (
            f"*Alert:* {alert.title}\n"
            f"*Severity:* {alert.severity}\n"
            f"*Source:* {alert.source}\n"
            f"*Status:* {alert.status}\n"
        )

        if alert.source_ip:
            message += f"*Source IP:* {alert.source_ip}\n"

        if alert.description:
            message += f"*Description:* {alert.description}\n"

        return await self.send_slack_notification(
            message=message,
            severity=alert.severity,
            alert_id=str(alert.id) if hasattr(alert, 'id') else None
        )


# Global instance
notification_service = NotificationService()