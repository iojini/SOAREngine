from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    """Severity levels for security alerts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Processing status of an alert."""
    PENDING = "pending"
    PROCESSING = "processing"
    ENRICHED = "enriched"
    COMPLETED = "completed"
    FAILED = "failed"


class AlertSource(str, Enum):
    """Common sources of security alerts."""
    EDR = "edr"
    SIEM = "siem"
    FIREWALL = "firewall"
    IDS = "ids"
    EMAIL = "email"
    CUSTOM = "custom"


class Alert(BaseModel):
    """A security alert to be processed by SOAREngine."""
    id: Optional[str] = None
    title: str = Field(..., description="Brief description of the alert")
    description: Optional[str] = Field(None, description="Detailed alert information")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    source: AlertSource = Field(..., description="System that generated the alert")
    source_ip: Optional[str] = Field(None, description="Source IP address involved")
    destination_ip: Optional[str] = Field(None, description="Destination IP address involved")
    domain: Optional[str] = Field(None, description="Domain name involved")
    file_hash: Optional[str] = Field(None, description="File hash (MD5/SHA256) involved")
    status: AlertStatus = Field(default=AlertStatus.PENDING, description="Processing status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    enrichment_data: Optional[dict] = Field(default=None, description="Data from threat intel enrichment")


class AlertCreate(BaseModel):
    """Schema for creating a new alert (without auto-generated fields)."""
    title: str = Field(..., description="Brief description of the alert")
    description: Optional[str] = Field(None, description="Detailed alert information")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    source: AlertSource = Field(..., description="System that generated the alert")
    source_ip: Optional[str] = Field(None, description="Source IP address involved")
    destination_ip: Optional[str] = Field(None, description="Destination IP address involved")
    domain: Optional[str] = Field(None, description="Domain name involved")
    file_hash: Optional[str] = Field(None, description="File hash (MD5/SHA256) involved")