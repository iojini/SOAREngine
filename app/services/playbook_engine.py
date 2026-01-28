from typing import Dict, List, Optional
from uuid import uuid4

from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.playbook import (
    Playbook,
    PlaybookCreate,
    PlaybookExecutionResult,
    ActionType,
)
from app.services.enrichment import enrichment_service


class PlaybookEngine:
    """Engine for managing and executing security playbooks."""

    def __init__(self):
        self.playbooks: Dict[str, Playbook] = {}
        self._create_default_playbooks()

    def _create_default_playbooks(self):
        """Create some default playbooks to demonstrate functionality."""
        
        # Playbook 1: High severity auto-enrichment
        high_severity_playbook = Playbook(
            id=str(uuid4()),
            name="High Severity Auto-Enrich",
            description="Automatically enrich all high/critical severity alerts",
            enabled=True,
            trigger={
                "min_severity": "high"
            },
            actions=[
                {"type": ActionType.ENRICH_ALL},
                {"type": ActionType.NOTIFY_SLACK, "config": {"channel": "#security-alerts"}}
            ]
        )
        self.playbooks[high_severity_playbook.id] = high_severity_playbook

        # Playbook 2: EDR alert response
        edr_playbook = Playbook(
            id=str(uuid4()),
            name="EDR Alert Response",
            description="Handle alerts from EDR systems",
            enabled=True,
            trigger={
                "source_types": ["edr"]
            },
            actions=[
                {"type": ActionType.ENRICH_ALL},
                {"type": ActionType.CREATE_TICKET, "config": {"priority": "high"}}
            ]
        )
        self.playbooks[edr_playbook.id] = edr_playbook

        # Playbook 3: Malware keyword detection
        malware_playbook = Playbook(
            id=str(uuid4()),
            name="Malware Investigation",
            description="Triggered when malware-related keywords detected",
            enabled=True,
            trigger={
                "keywords": ["malware", "ransomware", "trojan", "virus"]
            },
            actions=[
                {"type": ActionType.ENRICH_ALL},
                {"type": ActionType.ISOLATE_HOST, "config": {"auto": False}},
                {"type": ActionType.NOTIFY_SLACK, "config": {"channel": "#incident-response"}}
            ]
        )
        self.playbooks[malware_playbook.id] = malware_playbook

    def create_playbook(self, playbook_data: PlaybookCreate) -> Playbook:
        """Create a new playbook."""
        playbook_id = str(uuid4())
        playbook = Playbook(id=playbook_id, **playbook_data.model_dump())
        self.playbooks[playbook_id] = playbook
        return playbook

    def get_playbook(self, playbook_id: str) -> Optional[Playbook]:
        """Get a playbook by ID."""
        return self.playbooks.get(playbook_id)

    def list_playbooks(self) -> List[Playbook]:
        """List all playbooks."""
        return list(self.playbooks.values())

    def delete_playbook(self, playbook_id: str) -> bool:
        """Delete a playbook."""
        if playbook_id in self.playbooks:
            del self.playbooks[playbook_id]
            return True
        return False

    def _check_trigger(self, playbook: Playbook, alert: Alert) -> bool:
        """Check if an alert matches a playbook's trigger conditions."""
        if not playbook.enabled:
            return False

        trigger = playbook.trigger

        # Check severity
        if trigger.min_severity:
            severity_order = ["low", "medium", "high", "critical"]
            min_idx = severity_order.index(trigger.min_severity)
            alert_idx = severity_order.index(alert.severity.value)
            if alert_idx < min_idx:
                return False

        # Check source types
        if trigger.source_types:
            if alert.source.value not in trigger.source_types:
                return False

        # Check keywords
        if trigger.keywords:
            text = f"{alert.title} {alert.description or ''}".lower()
            if not any(kw.lower() in text for kw in trigger.keywords):
                return False

        return True

    def find_matching_playbooks(self, alert: Alert) -> List[Playbook]:
        """Find all playbooks that match an alert."""
        return [pb for pb in self.playbooks.values() if self._check_trigger(pb, alert)]

    async def _execute_action(self, action_type: ActionType, alert: Alert, config: dict) -> dict:
        """Execute a single playbook action."""
        result = {
            "action": action_type.value,
            "success": True,
            "message": ""
        }

        try:
            if action_type == ActionType.ENRICH_ALL:
                enrichment = await enrichment_service.enrich_alert(alert)
                alert.enrichment_data = enrichment
                result["message"] = f"Enriched {len(enrichment)} indicators"

            elif action_type == ActionType.ENRICH_IP:
                if alert.source_ip:
                    data = await enrichment_service.enrich_ip(alert.source_ip)
                    alert.enrichment_data = alert.enrichment_data or {}
                    alert.enrichment_data["source_ip"] = data
                    result["message"] = f"Enriched IP {alert.source_ip}"
                else:
                    result["message"] = "No source IP to enrich"

            elif action_type == ActionType.ENRICH_DOMAIN:
                if alert.domain:
                    data = await enrichment_service.enrich_domain(alert.domain)
                    alert.enrichment_data = alert.enrichment_data or {}
                    alert.enrichment_data["domain"] = data
                    result["message"] = f"Enriched domain {alert.domain}"
                else:
                    result["message"] = "No domain to enrich"

            elif action_type == ActionType.NOTIFY_SLACK:
                channel = config.get("channel", "#alerts") if config else "#alerts"
                # Mock Slack notification
                result["message"] = f"Slack notification sent to {channel}"

            elif action_type == ActionType.CREATE_TICKET:
                priority = config.get("priority", "medium") if config else "medium"
                # Mock ticket creation
                result["message"] = f"Ticket created with {priority} priority"

            elif action_type == ActionType.BLOCK_IP:
                if alert.source_ip:
                    # Mock IP blocking
                    result["message"] = f"IP {alert.source_ip} blocked at firewall"
                else:
                    result["message"] = "No IP to block"

            elif action_type == ActionType.ISOLATE_HOST:
                auto = config.get("auto", False) if config else False
                if auto:
                    result["message"] = "Host isolation initiated"
                else:
                    result["message"] = "Host isolation recommended (manual approval required)"

        except Exception as e:
            result["success"] = False
            result["message"] = str(e)

        return result

    async def execute_playbook(self, playbook: Playbook, alert: Alert) -> PlaybookExecutionResult:
        """Execute a playbook against an alert."""
        actions_executed = []
        overall_success = True

        alert.status = AlertStatus.PROCESSING

        for action in playbook.actions:
            action_result = await self._execute_action(
                action.type,
                alert,
                action.config
            )
            actions_executed.append(action_result)
            if not action_result["success"]:
                overall_success = False

        alert.status = AlertStatus.COMPLETED if overall_success else AlertStatus.FAILED

        return PlaybookExecutionResult(
            playbook_id=playbook.id,
            playbook_name=playbook.name,
            alert_id=alert.id,
            success=overall_success,
            actions_executed=actions_executed
        )

    async def run_playbooks_for_alert(self, alert: Alert) -> List[PlaybookExecutionResult]:
        """Find and run all matching playbooks for an alert."""
        matching = self.find_matching_playbooks(alert)
        results = []

        for playbook in matching:
            result = await self.execute_playbook(playbook, alert)
            results.append(result)

        return results


# Global instance
playbook_engine = PlaybookEngine()