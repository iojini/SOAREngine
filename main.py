from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.alerts import router as alerts_router
from app.api.playbooks import router as playbooks_router
from app.api.mitre import router as mitre_router
from app.api.notifications import router as notifications_router
from app.config import get_settings
from app.database.db import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Security Orchestration, Automation & Response Platform",
    version=settings.app_version,
    lifespan=lifespan
)

# Register routers
app.include_router(alerts_router)
app.include_router(playbooks_router)
app.include_router(mitre_router)
app.include_router(notifications_router)

# Add Prometheus metrics
if settings.metrics_enabled:
    Instrumentator().instrument(app).expose(app)


@app.get("/health")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


@app.get("/config")
def get_config():
    """Get non-sensitive configuration info."""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug,
        "metrics_enabled": settings.metrics_enabled,
        "playbook_auto_run": settings.playbook_auto_run,
        "enrichment_timeout": settings.enrichment_timeout,
        "integrations": {
            "abuseipdb": settings.abuseipdb_api_key is not None,
            "virustotal": settings.virustotal_api_key is not None,
            "slack": settings.slack_webhook_url is not None,
            "ticketing": settings.ticketing_enabled
        }
    }