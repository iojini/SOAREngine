from typing import List, Set

from app.models.alert import Alert
from app.models.mitre import (
    MitreTechnique,
    AlertMitreMapping,
    MITRE_TECHNIQUES,
    KEYWORD_TECHNIQUE_MAP,
)


class MitreMapper:
    """Service for mapping alerts to MITRE ATT&CK techniques."""

    def __init__(self):
        self.techniques = MITRE_TECHNIQUES
        self.keyword_map = KEYWORD_TECHNIQUE_MAP

    def map_alert(self, alert: Alert) -> AlertMitreMapping:
        """Map an alert to relevant MITRE ATT&CK techniques."""
        # Combine title and description for analysis
        text = f"{alert.title} {alert.description or ''}".lower()
        
        # Find matching technique IDs
        matched_ids: Set[str] = set()
        
        for keyword, technique_ids in self.keyword_map.items():
            if keyword in text:
                matched_ids.update(technique_ids)
        
        # Convert IDs to full technique objects
        techniques: List[MitreTechnique] = []
        for tech_id in matched_ids:
            if tech_id in self.techniques:
                techniques.append(self.techniques[tech_id])
        
        # Determine confidence based on number of matches
        if len(techniques) >= 3:
            confidence = "high"
        elif len(techniques) >= 1:
            confidence = "medium"
        else:
            confidence = "low"
        
        return AlertMitreMapping(
            alert_id=alert.id,
            techniques=techniques,
            confidence=confidence
        )

    def get_technique(self, technique_id: str) -> MitreTechnique | None:
        """Get a specific MITRE ATT&CK technique by ID."""
        return self.techniques.get(technique_id)

    def list_techniques(self) -> List[MitreTechnique]:
        """List all available MITRE ATT&CK techniques."""
        return list(self.techniques.values())

    def get_techniques_by_tactic(self, tactic: str) -> List[MitreTechnique]:
        """Get all techniques for a specific tactic."""
        return [
            tech for tech in self.techniques.values()
            if tech.tactic.lower() == tactic.lower()
        ]


# Global instance
mitre_mapper = MitreMapper()