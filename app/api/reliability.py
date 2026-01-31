from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.api_key import verify_api_key
from app.services.reliability import (
    dead_letter_queue,
    enrichment_circuit,
    notification_circuit,
    OperationType,
)

router = APIRouter(
    prefix="/reliability",
    tags=["Reliability"],
    dependencies=[Depends(verify_api_key)]
)


class DLQStats(BaseModel):
    """Dead-letter queue statistics."""
    total_entries: int
    max_size: int
    by_type: dict


class CircuitBreakerStatus(BaseModel):
    """Circuit breaker status."""
    name: str
    state: str
    failure_count: int
    failure_threshold: int
    recovery_timeout: int
    last_failure: Optional[str] = None


class ReliabilityStatus(BaseModel):
    """Overall reliability status."""
    dead_letter_queue: DLQStats
    circuit_breakers: list[CircuitBreakerStatus]


@router.get("/status", response_model=ReliabilityStatus)
async def get_reliability_status() -> ReliabilityStatus:
    """Get overall reliability status including DLQ and circuit breakers."""
    dlq_stats = await dead_letter_queue.get_stats()
    enrichment_status = await enrichment_circuit.get_status()
    notification_status = await notification_circuit.get_status()

    return ReliabilityStatus(
        dead_letter_queue=DLQStats(**dlq_stats),
        circuit_breakers=[
            CircuitBreakerStatus(**enrichment_status),
            CircuitBreakerStatus(**notification_status),
        ]
    )


@router.get("/dlq")
async def get_dead_letter_queue(
    operation_type: Optional[str] = None
) -> list[dict]:
    """Get all entries in the dead-letter queue."""
    if operation_type:
        try:
            op_type = OperationType(operation_type)
            return await dead_letter_queue.get_by_type(op_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid operation type. Valid types: {[t.value for t in OperationType]}"
            )
    return await dead_letter_queue.get_all()


@router.delete("/dlq/{entry_id}")
async def remove_dlq_entry(entry_id: str) -> dict:
    """Remove an entry from the dead-letter queue."""
    removed = await dead_letter_queue.remove(entry_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Entry not found")
    return {"message": "Entry removed", "id": entry_id}


@router.delete("/dlq")
async def clear_dead_letter_queue() -> dict:
    """Clear all entries from the dead-letter queue."""
    count = await dead_letter_queue.clear()
    return {"message": f"Cleared {count} entries from DLQ"}


@router.get("/circuits")
async def get_circuit_breakers() -> list[CircuitBreakerStatus]:
    """Get status of all circuit breakers."""
    enrichment_status = await enrichment_circuit.get_status()
    notification_status = await notification_circuit.get_status()
    return [
        CircuitBreakerStatus(**enrichment_status),
        CircuitBreakerStatus(**notification_status),
    ]