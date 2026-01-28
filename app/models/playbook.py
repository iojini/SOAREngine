from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Types of actions a playbook can perform."""
    ENRICH_IP = "enrich_ip"
    ENRICH_DOMAIN = "enrich_domain"
    ENRICH_ALL = "enrich_all"
    NOTIFY_SLACK = "notify_slack"
    CREATE_TICKET = "create_ticket"
    BLOCK_IP = "block_ip"
    ISOLATE_HOST = "isolate_host"


class PlaybookAction(BaseModel):
    """A single action within a playbook."""
    type: ActionType = Field(..., description="Type of action to perform")
    config: Optional[dict] = Field(default=None, description="Action-specific configuration")


class TriggerCondition(BaseModel):
    """Conditions that determine when a playbook runs."""
    min_severity: Optional[str] = Field(None, description="Minimum severity to trigger (low/medium/high/critical)")
    source_types: Optional[List[str]] = Field(None, description="Alert sources that trigger this playbook")
    keywords: Optional[List[str]] = Field(None, description="Keywords in title/description that trigger")


class Playbook(BaseModel):
    """An automated response playbook."""
    id: Optional[str] = None
    name: str = Field(..., description="Playbook name")
    description: Optional[str] = Field(None, description="What this playbook does")
    enabled: bool = Field(default=True, description="Whether playbook is active")
    trigger: TriggerCondition = Field(..., description="Conditions to trigger this playbook")
    actions: List[PlaybookAction] = Field(..., description="Actions to execute in order")


class PlaybookCreate(BaseModel):
    """Schema for creating a new playbook."""
    name: str = Field(..., description="Playbook name")
    description: Optional[str] = Field(None, description="What this playbook does")
    enabled: bool = Field(default=True, description="Whether playbook is active")
    trigger: TriggerCondition = Field(..., description="Conditions to trigger this playbook")
    actions: List[PlaybookAction] = Field(..., description="Actions to execute in order")


class PlaybookExecutionResult(BaseModel):
    """Result of executing a playbook."""
    playbook_id: str
    playbook_name: str
    alert_id: str
    success: bool
    actions_executed: List[dict]
    error: Optional[str] = None