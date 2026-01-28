from typing import List
from fastapi import APIRouter, HTTPException

from app.models.playbook import Playbook, PlaybookCreate, PlaybookExecutionResult
from app.services.playbook_engine import playbook_engine

router = APIRouter(prefix="/playbooks", tags=["Playbooks"])


@router.post("/", response_model=Playbook)
def create_playbook(playbook_data: PlaybookCreate) -> Playbook:
    """Create a new playbook."""
    return playbook_engine.create_playbook(playbook_data)


@router.get("/", response_model=List[Playbook])
def list_playbooks() -> List[Playbook]:
    """Get all playbooks."""
    return playbook_engine.list_playbooks()


@router.get("/{playbook_id}", response_model=Playbook)
def get_playbook(playbook_id: str) -> Playbook:
    """Get a specific playbook by ID."""
    playbook = playbook_engine.get_playbook(playbook_id)
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook not found")
    return playbook


@router.delete("/{playbook_id}")
def delete_playbook(playbook_id: str) -> dict:
    """Delete a playbook."""
    if not playbook_engine.delete_playbook(playbook_id):
        raise HTTPException(status_code=404, detail="Playbook not found")
    return {"message": "Playbook deleted successfully"}