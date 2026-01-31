import json
import asyncio
from datetime import datetime
from typing import Any, Callable, Optional
from functools import wraps
from enum import Enum

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log,
)
import logging

logger = logging.getLogger(__name__)


class OperationType(str, Enum):
    """Types of operations that can fail."""
    ENRICHMENT = "enrichment"
    NOTIFICATION = "notification"
    PLAYBOOK = "playbook"
    WEBHOOK = "webhook"


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class DeadLetterQueue:
    """
    In-memory dead-letter queue for failed operations.
    In production, use Redis, RabbitMQ, or a database.
    """
    
    def __init__(self, max_size: int = 1000):
        self._queue: list[dict] = []
        self._max_size = max_size
        self._lock = asyncio.Lock()
    
    async def add(
        self,
        operation_type: OperationType,
        payload: dict,
        error: str,
        alert_id: Optional[str] = None
    ) -> dict:
        """Add a failed operation to the dead-letter queue."""
        async with self._lock:
            entry = {
                "id": f"dlq-{datetime.utcnow().timestamp()}",
                "operation_type": operation_type.value,
                "payload": payload,
                "error": error,
                "alert_id": alert_id,
                "created_at": datetime.utcnow().isoformat(),
                "retry_count": 0,
                "status": "pending"
            }
            
            # Remove oldest if at capacity
            if len(self._queue) >= self._max_size:
                self._queue.pop(0)
            
            self._queue.append(entry)
            logger.warning(
                f"Added to DLQ: {operation_type.value} for alert {alert_id}. "
                f"Error: {error}. Queue size: {len(self._queue)}"
            )
            return entry
    
    async def get_all(self) -> list[dict]:
        """Get all entries in the dead-letter queue."""
        async with self._lock:
            return self._queue.copy()
    
    async def get_by_type(self, operation_type: OperationType) -> list[dict]:
        """Get entries by operation type."""
        async with self._lock:
            return [e for e in self._queue if e["operation_type"] == operation_type.value]
    
    async def remove(self, entry_id: str) -> bool:
        """Remove an entry from the queue."""
        async with self._lock:
            for i, entry in enumerate(self._queue):
                if entry["id"] == entry_id:
                    self._queue.pop(i)
                    return True
            return False
    
    async def clear(self) -> int:
        """Clear all entries and return count."""
        async with self._lock:
            count = len(self._queue)
            self._queue.clear()
            return count
    
    async def get_stats(self) -> dict:
        """Get queue statistics."""
        async with self._lock:
            by_type = {}
            for entry in self._queue:
                op_type = entry["operation_type"]
                by_type[op_type] = by_type.get(op_type, 0) + 1
            
            return {
                "total_entries": len(self._queue),
                "max_size": self._max_size,
                "by_type": by_type
            }


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures.
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._half_open_calls = 0
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitState:
        return self._state
    
    async def can_execute(self) -> bool:
        """Check if the circuit allows execution."""
        async with self._lock:
            if self._state == CircuitState.CLOSED:
                return True
            
            if self._state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if self._last_failure_time:
                    elapsed = (datetime.utcnow() - self._last_failure_time).seconds
                    if elapsed >= self.recovery_timeout:
                        self._state = CircuitState.HALF_OPEN
                        self._half_open_calls = 0
                        logger.info(f"Circuit {self.name}: OPEN -> HALF_OPEN")
                        return True
                return False
            
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls < self.half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                return False
            
            return False
    
    async def record_success(self):
        """Record a successful call."""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.half_open_max_calls:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
                    self._success_count = 0
                    logger.info(f"Circuit {self.name}: HALF_OPEN -> CLOSED")
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0
    
    async def record_failure(self):
        """Record a failed call."""
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = datetime.utcnow()
            
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
                logger.warning(f"Circuit {self.name}: HALF_OPEN -> OPEN")
            elif self._state == CircuitState.CLOSED:
                if self._failure_count >= self.failure_threshold:
                    self._state = CircuitState.OPEN
                    logger.warning(f"Circuit {self.name}: CLOSED -> OPEN (failures: {self._failure_count})")
    
    async def get_status(self) -> dict:
        """Get circuit breaker status."""
        async with self._lock:
            return {
                "name": self.name,
                "state": self._state.value,
                "failure_count": self._failure_count,
                "failure_threshold": self.failure_threshold,
                "recovery_timeout": self.recovery_timeout,
                "last_failure": self._last_failure_time.isoformat() if self._last_failure_time else None
            }


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


def with_retry(
    max_attempts: int = 3,
    min_wait: float = 1,
    max_wait: float = 10,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for adding retry logic with exponential backoff.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            last_exception = None
            
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    last_exception = e
                    
                    if attempt < max_attempts:
                        wait_time = min(max_wait, min_wait * (2 ** (attempt - 1)))
                        logger.warning(
                            f"Retry {attempt}/{max_attempts} for {func.__name__} "
                            f"after {wait_time}s. Error: {str(e)}"
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(
                            f"All {max_attempts} retries failed for {func.__name__}. "
                            f"Last error: {str(e)}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


# Global instances
dead_letter_queue = DeadLetterQueue()
enrichment_circuit = CircuitBreaker("enrichment", failure_threshold=5, recovery_timeout=60)
notification_circuit = CircuitBreaker("notification", failure_threshold=3, recovery_timeout=30)