from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.alerts import router as alerts_router
from app.api.playbooks import router as playbooks_router
from app.api.mitre import router as mitre_router

app = FastAPI(
    title="SOAREngine",
    description="Security Orchestration, Automation & Response Platform",
    version="0.1.0"
)

# Register routers
app.include_router(alerts_router)
app.include_router(playbooks_router)
app.include_router(mitre_router)

# Add Prometheus metrics
Instrumentator().instrument(app).expose(app)


@app.get("/health")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy", "service": "SOAREngine"}