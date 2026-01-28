from fastapi import FastAPI

from app.api.alerts import router as alerts_router
from app.api.playbooks import router as playbooks_router

app = FastAPI(
    title="SOAREngine",
    description="Security Orchestration, Automation & Response Platform",
    version="0.1.0"
)

# Register routers
app.include_router(alerts_router)
app.include_router(playbooks_router)


@app.get("/health")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy", "service": "SOAREngine"}